import os
import requests
import math
import time
import io
from ..client.api_client import ApiClient
from typing import Optional, List, Dict, Any, Union
from dataclasses import asdict, is_dataclass
from pathlib import Path
from ..types.file_upload_types import (
    FileType,
    CreateMultipartUploadFormValues,
    MultipartUpload,
    CompleteMultipartUploadFormValues,
    RefreshMultipartUpload,
    CompletedPart,
    RefreshMultipartUploadUrlFormValues,
    UploadFileOptions,
    CompleteFileResponseWrapper,
)
from ..types.dream_types import Dream
from ..types.types import T

PART_SIZE = 1024 * 1024 * 200
MAX_RETRIES = 3
DOWNLOAD_CHUNCK_SIZE = 20 * 1024 * 1024


class ProgressTracker(io.BytesIO):
    def __init__(self, data, callback, interval, base_uploaded, total_size):
        super().__init__(data)
        self.callback = callback
        self.interval = interval
        self.base_uploaded = base_uploaded
        self.total_size = total_size
        self.last_report = time.time()
        
    def read(self, size=-1):
        chunk = super().read(size)
        if self.callback and self.total_size > 0:
            current_time = time.time()
            if current_time - self.last_report >= self.interval:
                uploaded = self.base_uploaded + self.tell()
                percentage = (uploaded / self.total_size) * 100
                try:
                    self.callback(uploaded, self.total_size, percentage)
                except Exception as e:
                    print(f"Warning: Progress callback error: {e}")
                self.last_report = current_time
        return chunk


def calculate_total_parts(file_size: int) -> int:
    """
    Calculates total upload parts
    Args:
        file_size (int): file size
    Returns:
        int: total number of parts
    """
    return max(math.ceil(file_size / PART_SIZE), 1)


class FileClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def _get_create_upload_endpoint(
        self, type: FileType, uuid: Optional[str] = None
    ) -> str:
        """
        Generates the endpoint for creating a multipart upload based on the file type
        Args:
            type (FileType): Type of the file
            uuid (Optional[str]): UUID of the source (if applicable)
        Returns:
            str: Endpoint for creating multipart upload
        """
        if type == FileType.DREAM and not uuid:
            return "/dream/create-multipart-upload"
        elif type in [FileType.DREAM, FileType.FILMSTRIP, FileType.THUMBNAIL]:
            return f"/dream/{uuid}/create-multipart-upload"
        elif type == FileType.KEYFRAME:
            return f"/keyframe/{uuid}/image/init"
        else:
            return f""

    def _get_refresh_url_endpoint(
        self, type: FileType, uuid: Optional[str] = None
    ) -> str:
        """
        Generates the endpoint for refreshing a multipart upload URL
        Args:
            uuid (str): UUID of the resource
        Returns:
            str: Endpoint for refreshing URL
        """
        if type in [FileType.DREAM, FileType.FILMSTRIP, FileType.THUMBNAIL]:
            return f"/dream/{uuid}/create-multipart-upload"
        elif type == FileType.KEYFRAME:
            return f""
        else:
            return f""

    def _get_complete_upload_endpoint(
        self, type: FileType, uuid: Optional[str] = None
    ) -> str:
        """
        Generates the endpoint for completing a multipart upload
        Args:
            uuid (str): UUID of the resource
        Returns:
            str: Endpoint for completing upload
        """
        if type in [FileType.DREAM, FileType.FILMSTRIP, FileType.THUMBNAIL]:
            return f"/dream/{uuid}/complete-multipart-upload"
        elif type == FileType.KEYFRAME:
            return f"/keyframe/{uuid}/image/complete"
        else:
            return f""

    def _build_create_payload(
        self,
        type: FileType,
        path: Path,
        parts: Optional[int] = None,
        options: Optional[UploadFileOptions] = None,
    ) -> CreateMultipartUploadFormValues:
        """
        Builds the payload for the upload request based on the file type and options.
        Args:
            type (FileType): Type of the file.
            options (UploadFileOptions): Options for the upload.
        Returns:
            Dict[str, Any]: Payload for the upload request.
        """
        # Extract common options
        file_extension = path.suffix.lstrip(".")
        payload: CreateMultipartUploadFormValues = {
            "parts": parts,
            "extension": file_extension,
            **({"uuid": options.get("uuid")} if options is not None else {}),
        }

        # Add type-specific fields to payload
        if type == FileType.DREAM:
            # dream name, needed only on FileType.DREAM type
            dream_name = None
            if options and options.get("name"):
                dream_name = options.get("name")
            else:
                dream_name = path.stem

            payload.update(
                {
                    "name": dream_name,
                    "type": type,
                    **(
                        {
                            k: v
                            for k, v in (options or {}).items()
                            if k in ["nsfw", "processed"]
                        }
                    ),
                }
            )
        elif type == FileType.THUMBNAIL:
            payload.update(
                {
                    "type": type,
                }
            )
        # frameNumber must be required for FILMSTRIP
        elif type == FileType.FILMSTRIP:
            payload.update(
                {
                    "type": type,
                    **(
                        {"frameNumber": options.get("frame_number")}
                        if options is not None
                        else {}
                    ),
                }
            )
        elif type == FileType.KEYFRAME:
            payload.update({})

        return payload

    def _build_refresh_payload(
        self,
        type: FileType,
        upload_id: str,
        part_number: int,
        file_extension: str,
        options: UploadFileOptions,
    ) -> RefreshMultipartUploadUrlFormValues:
        payload: RefreshMultipartUploadUrlFormValues = {
            "type": type,
            "uploadId": upload_id,
            "part": part_number,
            "extension": file_extension,
            "parts": 1,
        }

        # Add optional fields based on file type
        if type == FileType.DREAM:
            payload.update(
                {
                    **(
                        {"processed": options.get("processed")}
                        if options is not None
                        else {}
                    ),
                }
            )
        elif type == FileType.FILMSTRIP:
            payload.update(
                {
                    **(
                        {"frameNumber": options.get("frame_number")}
                        if options is not None
                        else {}
                    ),
                }
            )

        return payload

    def _build_complete_payload(
        self,
        type: FileType,
        path: Path,
        upload_id: str,
        parts: List[CompletedPart],
        options: Optional[UploadFileOptions] = None,
    ) -> CompleteMultipartUploadFormValues:
        """
        Builds the payload for the complete multipart upload request.
        Args:
            upload_id (str): The ID of the multipart upload.
            parts (List[Dict[str, Any]]): List of completed parts with ETags and part numbers.
            file_extension (str): The file extension (e.g., "mp4").
            type (FileType): The type of the file.
            options (UploadFileOptions): Options for the upload.
        Returns:
            Dict[str, Any]: The payload for the complete multipart upload request.
        """
        # Extract common options
        file_extension = path.suffix.lstrip(".")

        payload: CompleteMultipartUploadFormValues = {
            "uploadId": upload_id,
            "parts": parts,
            "extension": file_extension,
            "type": type,
        }

        # Add optional fields based on file type
        if type == FileType.DREAM:
            # dream name, needed only on FileType.DREAM type
            dream_name = None
            if options and options.get("name"):
                dream_name = options.get("name")
            else:
                dream_name = path.stem
            payload.update(
                {
                    "name": dream_name,
                    **(
                        {
                            k: v
                            for k, v in (options or {}).items()
                            if k in ["nsfw", "processed"]
                        }
                    ),
                }
            )
        elif type == FileType.FILMSTRIP:
            payload.update(
                {
                    **(
                        {"frameNumber": options.get("frame_number")}
                        if options is not None
                        else {}
                    ),
                }
            )
        elif type == FileType.THUMBNAIL:
            # No additional fields for THUMBNAIL
            pass
        elif type == FileType.KEYFRAME:
            # No additional fields for KEYFRAME
            pass

        return payload

    def _make_upload_request(
        self,
        endpoint: str,
        request_data: Union[
            Dict[str, Any], Any
        ],  # or Dict[str, Any] | Any in Python 3.10+
    ) -> T:
        """
        Generic helper function to handle multipart upload requests.
        Args:
            endpoint (str): The API endpoint.
            request_data (Any): The request data (dataclass instance).
            response_type (Type[T]): The expected response type.
        Returns:
            T: The deserialized response data.
        """

        # Make the API call
        response = self.api_client.post(endpoint, request_data)
        return response["data"]

    def _create_multipart_upload(
        self,
        endpoint: str,
        request_data: CreateMultipartUploadFormValues,
    ) -> MultipartUpload:
        """
        Creates multipart upload.
        Args:
            endpoint (str): The API endpoint.
            request_data (CreateMultipartUploadFormValues): Multipart upload request form.
        Returns:
            MultipartUpload: Multipart upload data.
        """
        return self._make_upload_request(endpoint, request_data)

    def _refresh_multipart_upload(
        self,
        endpoint: str,
        request_data: RefreshMultipartUploadUrlFormValues,
    ) -> RefreshMultipartUpload:
        """
        Refreshes multipart upload URL.
        Args:
            endpoint (str): The API endpoint.
            request_data (RefreshMultipartUploadUrlFormValues): Request multipart upload request form.
        Returns:
            RefreshMultipartUpload: Refresh multipart upload URL data.
        """
        return self._make_upload_request(endpoint, request_data)

    def _complete_multipart_upload(
        self,
        endpoint: str,
        request_data: CompleteMultipartUploadFormValues,
    ) -> CompleteFileResponseWrapper:
        """
        Completes multipart upload.
        Args:
            endpoint (str): The API endpoint.
            request_data (CompleteMultipartUploadFormValues): Complete multipart upload request form.
        Returns:
            CompleteFileResponseWrapper: Response after completing upload.
        """
        return self._make_upload_request(endpoint, request_data)

    def _upload_file_request(
        self,
        presigned_url: str,
        file_part: bytes,
        file_type: Optional[str] = None,
        progress_callback: Optional[Any] = None,
        progress_interval: float = 1.0,
        base_bytes_uploaded: int = 0,
        total_file_size: int = 0,
    ) -> Optional[str]:
        headers = {"Content-Type": file_type or ""}
        
        try:
            if progress_callback and total_file_size > 0:
                data = ProgressTracker(file_part, progress_callback, progress_interval, base_bytes_uploaded, total_file_size)
            else:
                data = file_part
                
            response = requests.put(
                presigned_url,
                data=data,
                headers=headers,
            )
            response.raise_for_status()
            etag = response.headers.get("etag", "")
            cleaned_etag = etag.strip('"')
            return cleaned_etag
        except requests.exceptions.RequestException as e:
            return None

    def download_file(
        self, 
        url: str, 
        file_path: Optional[str] = None,
        progress_callback: Optional[Any] = None,
        progress_interval: float = 1.0
    ) -> bool:
        """
        Downloads a file from a url to a path
        Args:
            url (str): URL to download from
            file_path (Optional[str]): Path to save file to (defaults to basename of URL)
            progress_callback (Optional[Callable]): Optional callback function for progress updates
            progress_interval (float): Interval in seconds between progress updates
        Returns:
            bool: True if download successful, False otherwise
        """
        if file_path is None:
            # Default to basename of URL if no path is provided
            file_path = os.path.basename(url)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            response = requests.get(url, stream=True)
            
            # Raise an error for bad status codes
            response.raise_for_status()

            # Try to get file size from response headers
            file_size = int(response.headers.get("content-length", 0))

            # In progress bytes downloaded
            bytes_downloaded = 0
            last_progress_time = time.time()

            # Write the content to a file
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNCK_SIZE):
                    if chunk:
                        file.write(chunk)
                        bytes_downloaded += len(chunk)

                    if file_size > 0:
                        current_time = time.time()
                        if progress_callback and (current_time - last_progress_time >= progress_interval):
                            progress_percentage = (bytes_downloaded / file_size) * 100
                            try:
                                progress_callback(bytes_downloaded, file_size, progress_percentage)
                            except Exception as e:
                                print(f"Warning: Progress callback error: {e}")
                            last_progress_time = current_time

            if progress_callback and file_size > 0:
                try:
                    progress_callback(file_size, file_size, 100.0)
                except Exception as e:
                    print(f"Warning: Progress callback error: {e}")
            
            # Verify the file was created and has content
            if os.path.exists(file_path):
                actual_size = os.path.getsize(file_path)
                return actual_size > 0
            else:
                return False

        except requests.exceptions.RequestException:
            return False
        except Exception:
            return False

    def _upload_file_part(
        self,
        uuid: str,
        type: FileType,
        upload_id: str,
        presigned_url: str,
        part_number: int,
        file_part: bytes,
        file_type: Optional[str] = None,
        options: Optional[UploadFileOptions] = None,
        progress_callback: Optional[Any] = None,
        progress_interval: float = 1.0,
        base_bytes_uploaded: int = 0,
        total_file_size: int = 0,
    ) -> Optional[str]:
        """
        Refreshes multipart upload part
        Args:
            uuid (str): resource uuid
            upload_id (str): generated multipart upload id
            presigned_url (str): presigned url to target request
            part_number (int): part number
            file_part (bytes): file part bytes
            file_type (str): file type
            progress_callback: callback for progress updates
            progress_interval: interval in seconds between progress updates
            base_bytes_uploaded: bytes already uploaded before this part
            total_file_size: total size of the file being uploaded
        Returns:
            str: etag str
        """
        attempt = 0
        url = presigned_url
        while attempt < MAX_RETRIES:
            result = self._upload_file_request(
                presigned_url=url, 
                file_part=file_part, 
                file_type=file_type,
                progress_callback=progress_callback,
                progress_interval=progress_interval,
                base_bytes_uploaded=base_bytes_uploaded,
                total_file_size=total_file_size,
            )
            if result is not None:
                return result
            else:
                # new attemp
                attempt += 1
                if attempt < MAX_RETRIES:
                    print(f"Retrying part {attempt + 1}.")
                    refresh_upload_endpoint = self._get_refresh_url_endpoint(type, uuid)
                    refresh_payload = self._build_refresh_payload(
                        type=type,
                        upload_id=upload_id,
                        part_number=part_number,
                        file_extension=file_type,
                        options=options,
                    )
                    refresh_result = self._refresh_multipart_upload(
                        endpoint=refresh_upload_endpoint, request_data=refresh_payload
                    )
                    url = refresh_result["urls"][0]
                else:
                    raise Exception(f"Upload failed. Max retries reached on part {part_number}")

    def upload_file(
        self,
        file_path: str,
        type: FileType,
        options: Optional[UploadFileOptions] = None,
    ) -> Dream | bool | Any:
        """
        This function should be made private in future versions.
        Complete function to upload file to s3 creating a resource on process.
        Args:
            file_path (str): file path
            type (FileType): type of file to upload
        Returns:
            Dream | bool | Any: created resource after completing upload
        """

        if type not in [
            FileType.DREAM,
            FileType.THUMBNAIL,
            FileType.FILMSTRIP,
            FileType.KEYFRAME,
        ]:
            raise Exception(f"Type not allowed.")

        path = Path(file_path)
        file_extension = path.suffix.lstrip(".")
        file_size = path.stat().st_size
        total_parts = calculate_total_parts(file_size)

        # Extract options
        uuid = options.get("uuid") if options else None

        # Create multipart upload
        create_upload_endpoint = self._get_create_upload_endpoint(type, uuid)
        create_payload = self._build_create_payload(
            type=type,
            parts=total_parts,
            path=path,
            options=options,
        )

        # create multipart upload
        multipart_upload: MultipartUpload = self._create_multipart_upload(
            endpoint=create_upload_endpoint, request_data=create_payload
        )

        # if type == FileType.DREAM and it doesn't have uuid (created on multipart request for dreams), set uuid
        if (
            uuid is None
            and type == FileType.DREAM
            and multipart_upload is not None
            and (dream := multipart_upload.get("dream")) is not None
        ):
            if not isinstance(dream, dict):
                raise Exception(f"Multipart upload dream is not a dict. Type: {type(dream)}, Value: {dream}")
            if "uuid" not in dream:
                raise Exception(f"Multipart upload dream object missing 'uuid' key. Dream: {dream}, MultipartUpload: {multipart_upload}")
            uuid = dream["uuid"]

        upload_id = multipart_upload["uploadId"]
        urls = multipart_upload["urls"]
        completed_parts: List[CompletedPart] = []

        progress_callback = options.get("progress_callback") if options else None
        progress_interval = options.get("progress_interval", 1.0) if options else 1.0

        # in progreess bytes uploaded
        bytes_uploaded = 0

        if progress_callback:
            try:
                progress_callback(0, file_size, 0.0)
            except Exception as e:
                print(f"Warning: Progress callback error: {e}")

        with open(file_path, "rb") as file:
            # iterates urls to upload each part and obtaining each etag
            for index, url in enumerate(urls):
                part_number = index + 1
                part_data = bytearray()
                

                if not part_data:
                    break

                # obtain etag from _upload_file_part function call
                etag = self._upload_file_part(
                    type=type,
                    uuid=uuid,
                    upload_id=upload_id,
                    part_number=part_number,
                    presigned_url=url,
                    file_part=part_data,
                    file_type=file_extension,
                    options=options,
                    progress_callback=progress_callback,
                    progress_interval=progress_interval,
                    base_bytes_uploaded=bytes_uploaded,
                    total_file_size=file_size,
                )
                completed_parts.append({"ETag": etag, "PartNumber": part_number})
                bytes_uploaded += len(part_data)

        # Build the payload
        complete_upload_endpoint = self._get_complete_upload_endpoint(type, uuid)

        complete_payload = self._build_complete_payload(
            upload_id=upload_id,
            parts=completed_parts,
            path=path,
            type=type,
            options=options,
        )

        # Complete upload request
        completed_upload = self._complete_multipart_upload(
            endpoint=complete_upload_endpoint, request_data=complete_payload
        )

        if progress_callback:
            try:
                progress_callback(file_size, file_size, 100.0)
            except Exception as e:
                print(f"Warning: Progress callback error: {e}")
        if type in [FileType.DREAM, FileType.FILMSTRIP, FileType.THUMBNAIL]:
            if "dream" not in completed_upload:
                raise Exception(f"Upload completed but response missing 'dream' key. Response: {completed_upload}")
            dream = completed_upload.get("dream")
            if not dream:
                raise Exception(f"Upload completed but dream object is None in response. Response: {completed_upload}")
            if not isinstance(dream, dict):
                raise Exception(f"Upload completed but dream is not a dict. Type: {type(dream)}, Value: {dream}")
            if "uuid" not in dream:
                raise Exception(f"Upload completed but dream object missing 'uuid' key. Dream: {dream}")
            return dream

        return True
