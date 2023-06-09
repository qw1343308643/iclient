import mimetypes
import os
import subprocess
import zipfile

from common.systemCommon import is_windows_or_linux
from config.errorCode import NetTestClientError, ERROR_CODE_ERROR


class DecompressingFile:
    @staticmethod
    def unFile(source_path, total_path, compression_type):
        if not os.path.exists(total_path):
            os.makedirs(total_path)
        c_type = {
            "zip": DecompressingFile.unzip_zip,
            "7z": DecompressingFile.unzip_7z,
            "tar": DecompressingFile.unzip_targz
        }
        func = c_type.get(compression_type)
        if func:
            func(source_path, total_path)
        else:
            raise NetTestClientError(ERROR_CODE_ERROR.UNKNOWN_DECOMPRESSION_TYPE.value)

    @staticmethod
    def unzip_zip(source_path, total_apth):
        currtPlatform = is_windows_or_linux()
        if currtPlatform == "windows":
            zipFile = zipfile.ZipFile(source_path)
            zipFile.extractall(total_apth)
            zipFile.close()
        elif currtPlatform == "linux":
            cmd = f'unzip -d "{total_apth}" "{source_path}"'
            print(cmd)
            ret = subprocess.run(cmd, shell=True, capture_output=True)
            if ret.returncode != 0:
                raise NetTestClientError(str(ERROR_CODE_ERROR.UNZIP_FAIL.value))

    @staticmethod
    def unzip_7z(source_path, total_apth):
        import py7zr
        with py7zr.SevenZipFile(source_path, mode='r') as z:
            z.extractall(total_apth)

    @staticmethod
    def unzip_targz(source_path, total_apth):
        cmd = f'tar -zxvf "{source_path}" -C "{total_apth}"'
        ret = subprocess.run(cmd, shell=True, capture_output=True)
        if ret.returncode != 0:
            raise NetTestClientError(str(ERROR_CODE_ERROR.UNZIP_FAIL.value))

    @staticmethod
    def get_compression_type(path):
        mimetype, _ = mimetypes.guess_type(path)
        print(f"{path} compression type:{mimetype}")
        if mimetype:
            if mimetype in ("application/zip", "application/x-zip-compressed"):
                return "zip"
            elif mimetype in ("application/x-7z-compressed"):
                return "7z"
            elif mimetype in ("application/x-rar-compressed"):
                return "rar"
            elif mimetype in ("application/x-tar"):
                return "tar"
            elif mimetype in ("application/gzip"):
                return "gzip"
            elif mimetype in ("application/x-bzip2"):
                return "bzip2"
            else:
                return None
        return None