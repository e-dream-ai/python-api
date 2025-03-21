import os
import requests
import math
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

# FILE PART SIZE
PART_SIZE = 1024 * 1024 * 200  # 200 MB
# UPLOAD PART MAX RETRIES
MAX_RETRIES = 3
# DOWNLOAD_CHUNCK_SIZE = 20 MB
DOWNLOAD_CHUNCK_SIZE = 20 * 1024 * 1024


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
            file_name = path.stem
            dream_name = file_name if type == FileType.DREAM else None

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
        """
        Builds the payload for the refresh multipart upload URL request.
        Args:
            type (FileType): The type of the file.
            upload_id (str): The ID of the multipart upload.
            part_number (int): The part number being refreshed.
            file_extension (str): The file extension (e.g., "mp4").
            options (UploadFileOptions): Options for the upload.
        Returns:
            Dict[str, Any]: The payload for the refresh multipart upload URL request.
        """
        # Base payload
        payload: RefreshMultipartUploadUrlFormValues = {
            "type": type,
            "uploadId": upload_id,
            "part": part_number,
            "extension": file_extension,
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
            file_name = path.stem
            dream_name = file_name if type == FileType.DREAM else None
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
    ) -> Optional[str]:
        """
        Upload file request to s3 using `requests`
        Args:
            presigned_url (str): presigned s3 url
            file_part (bytes): file part bytes
            file_type (str): file type
        Returns:
            Optional[str]: etag str
        """
        headers = {"Content-Type": file_type or ""}
        try:
            response = requests.put(
                presigned_url,
                data=file_part,
                headers=headers,
            )
            response.raise_for_status()
            # Extract and clean the ETag header
            etag = response.headers.get("etag", "")
            cleaned_etag = etag.strip('"')
            return cleaned_etag
        except requests.exceptions.RequestException as e:
            # print(f"An error occurred: {e}")
            return None

    def download_file(self, url: str, file_path: Optional[str] = None) -> bool:
        """
        Downloads a file from a url to a path
        """
        if file_path is None:
            # Default to basename of URL if no path is provided
            file_path = os.path.basename(url)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            # Send a HEAD request to get the content length
            head_response = requests.head(url)
            head_response.raise_for_status()
            file_size = int(head_response.headers.get("content-length", 0))

            # Send a GET request to the URL
            response = requests.get(url, stream=True)
            # Raise an error for bad status codes
            response.raise_for_status()

            # In progreess bytes downloaded
            bytes_downloaded = 0

            # Write the content to a file
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNCK_SIZE):
                    if chunk:
                        file.write(chunk)
                        bytes_downloaded += len(chunk)

                    progress_percentage = (bytes_downloaded / file_size) * 100
                    print(f"Download progress: {progress_percentage:.2f}%")

        except requests.RequestException as e:
            return False

        return True

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
        Returns:
            str: etag str
        """
        attempt = 0
        url = presigned_url
        while attempt < MAX_RETRIES:
            result = self._upload_file_request(
                presigned_url=url, file_part=file_part, file_type=file_type
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
                        uploadId=upload_id,
                        part=part_number,
                        extension=file_type,
                        options=options,
                    )
                    refresh_result = self._refresh_multipart_upload(
                        endpoint=refresh_upload_endpoint, request_data=refresh_payload
                    )
                    new_url = refresh_result.url
                    url = new_url
                else:
                    raise f"Upload failed. Max retries reached on part {file_part}"

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
        uuid = options.uuid if options else None

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
            uuid = dream["uuid"]

        upload_id = multipart_upload["uploadId"]
        urls = multipart_upload["urls"]
        completed_parts: List[CompletedPart] = []

        # in progreess bytes uploaded
        bytes_uploaded = 0

        with open(file_path, "rb") as file:
            # iterates urls to upload each part and obtaining each etag
            for index, url in enumerate(urls):
                part_number = index + 1
                part_data = file.read(PART_SIZE)

                # exit the loop if read all the data
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
                )
                completed_parts.append({"ETag": etag, "PartNumber": part_number})
                bytes_uploaded += len(part_data)
                progress_percentage = (bytes_uploaded / file_size) * 100
                print(f"Upload progress: {progress_percentage:.2f}%")

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

        print("Upload completed.")
        if type in [FileType.DREAM, FileType.FILMSTRIP, FileType.THUMBNAIL]:
            return completed_upload["dream"]

        return True
