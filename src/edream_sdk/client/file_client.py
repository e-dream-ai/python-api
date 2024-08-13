import requests
import math
from typing import Optional, List
from dataclasses import asdict
from pathlib import Path
from ..models.file_upload_types import (
    CreateMultipartUploadFormValues,
    MultipartUpload,
    CompleteMultipartUploadFormValues,
    RefreshMultipartUpload,
    CompletedPart,
    RefreshMultipartUploadUrlFormValues,
)
from ..models.dream_types import DreamResponseWrapper, Dream
from ..utils.api_utils import deserialize_api_response

part_size = 1024 * 1024 * 200  # 200 MB
retry_delay: float = 0.2
max_retries = 3


def calculate_total_parts(file_size: int) -> int:
    """
    Calculates total upload parts
    Args:
        file_size (int): file size
    Returns:
        int: total number of parts
    """
    return max(math.ceil(file_size / part_size), 1)


class FileClient:

    def upload_file_request(
        self,
        presigned_url: str,
        file_part: bytes,
        file_type: Optional[str] = None,
    ) -> Optional[str]:
        """
        Upload file request using `requests`
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

    def create_multipart_upload(
        self,
        request_data: CreateMultipartUploadFormValues,
    ) -> MultipartUpload:
        """
        Creates multipart upload
        Args:
            request_data (CreateMultipartUploadFormValues): multipart upload request form
        Returns:
            MultipartUpload: multipart upload data
        """
        request_data_dict = asdict(request_data)
        data = self._post(f"/dream/create-multipart-upload", request_data_dict)
        response = deserialize_api_response(data, MultipartUpload)
        multipart_upload = response.data
        return multipart_upload

    def refresh_multipart_upload_url(
        self,
        uuid: str,
        request_data: RefreshMultipartUploadUrlFormValues,
    ) -> RefreshMultipartUpload:
        """
        Refreshes multipart upload part
        Args:
            request_data (RefreshMultipartUploadUrlFormValues): request multipart upload request form
        Returns:
            RefreshMultipartUpload: refresh multipart upload url data
        """
        request_data_dict = asdict(request_data)
        data = self._post(
            f"/dream/{uuid}/refresh-multipart-upload-url", request_data_dict
        )
        response = deserialize_api_response(data, RefreshMultipartUpload)
        multipart_upload = response.data
        return multipart_upload

    def upload_file_part(
        self,
        uuid: str,
        upload_id: str,
        presigned_url: str,
        part_number: int,
        file_part: bytes,
        file_type: Optional[str] = None,
    ) -> Optional[str]:
        """
        Refreshes multipart upload part
        Args:
            uuid (str): dream uuid
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
        while attempt < max_retries:
            result = self.upload_file_request(
                presigned_url=url, file_part=file_part, file_type=file_type
            )
            if result is not None:
                return result
            else:
                print(f"Attempt {attempt + 1} failed.")
                attempt += 1
                if attempt < max_retries:
                    print(f"Retrying part {attempt + 1}.")
                    refresh_result = self.refresh_multipart_upload_url(
                        uuid,
                        RefreshMultipartUploadUrlFormValues(
                            uploadId=upload_id, part=part_number, extension=file_type
                        ),
                    )
                    new_url = refresh_result.url
                    url = new_url
                else:
                    raise f"Upload failed. Max retries reached on part {file_part}"

    def complete_multipart_upload(
        self,
        uuid: str,
        request_data: CompleteMultipartUploadFormValues,
    ) -> DreamResponseWrapper:
        """
        Completes multipart upload
        Args:
            uuid (str): dream uuid
            request_data (CompleteMultipartUploadFormValues): complete multipart upload request form
        Returns:
            DreamResponseWrapper: dream response after completing upload
        """
        request_data_dict = asdict(request_data)
        data = self._post(f"/dream/{uuid}/complete-multipart-upload", request_data_dict)
        response = deserialize_api_response(data, DreamResponseWrapper)
        return response.data

    def upload_file(self, file_path: str) -> Dream:
        """
        Complete function to upload file to s3 creating a dream on process
        Args:
            file_path (str): file path
        Returns:
            Dream: created dream after completing upload
        """
        path = Path(file_path)
        file_name = path.stem
        file_extension = path.suffix.lstrip(".")
        file_size = path.stat().st_size
        total_parts = calculate_total_parts(file_size)

        # create multipart upload
        multipart_upload: MultipartUpload = self.create_multipart_upload(
            CreateMultipartUploadFormValues(
                name=file_name, extension=file_extension, nsfw=False, parts=total_parts
            )
        )

        dream = multipart_upload.dream
        dream_uuid = dream.uuid
        upload_id = multipart_upload.uploadId
        urls = multipart_upload.urls
        completed_parts: List[CompletedPart] = []

        # in progreess bytes uploaded
        bytes_uploaded = 0

        with open(file_path, "rb") as file:
            # iterates urls to upload each part and obtaining each etag
            for index, url in enumerate(urls):
                part_number = index + 1
                part_data = file.read(part_size)

                # exit the loop if read all the data
                if not part_data:
                    break

                print(f"Uploading part {part_number}")
                etag = self.upload_file_part(
                    uuid=dream_uuid,
                    upload_id=upload_id,
                    part_number=part_number,
                    presigned_url=url,
                    file_part=part_data,
                    file_type=file_extension,
                )
                completed_parts.append(CompletedPart(ETag=etag, PartNumber=part_number))
                bytes_uploaded += len(part_data)
                progress_percentage = (bytes_uploaded / file_size) * 100
                print(f"Upload progress: {progress_percentage:.2f}%")

        # complete upload
        completed_upload = self.complete_multipart_upload(
            dream.uuid,
            CompleteMultipartUploadFormValues(
                uploadId=upload_id,
                extension=file_extension,
                name=file_name,
                parts=completed_parts,
            ),
        )

        print("Upload completed.")
        return completed_upload.dream
