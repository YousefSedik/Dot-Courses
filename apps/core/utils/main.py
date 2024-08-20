from django.contrib.auth import get_user_model
from pymediainfo import MediaInfo
from django import conf
import subprocess
import datetime
import os

User = get_user_model()


def get_duration(filename):
    media_info = MediaInfo.parse(filename)
    duration_in_ms = media_info.tracks[0].duration
    video_time = datetime.timedelta(seconds=int(duration_in_ms / 1000))
    return video_time


class CertificatePDF:
    def __init__(self, fullname, instructor_name, key, course_name):
        self.fullname = fullname
        self.instructor_name = instructor_name
        self.key = key
        self.course_name = course_name
        self.BASE_DIR = conf.settings.BASE_DIR
        self.CERTIFICATE_TEMPLATE_PATH = os.path.join(
            self.BASE_DIR, "media", "CERTIFICATE-TEMPLATE.pptx"
        )
        self.certificates_folder_path = os.path.join(
            self.BASE_DIR, "media", "certificates"
        )
        self.pptx_certificate_path = os.path.join(
            self.certificates_folder_path, f"{self.key}.pptx"
        )
        self.certificate_path = os.path.join(
            self.BASE_DIR, "media", "certificates", f"{self.key}.pdf"
        )

    def create_certificate_pdf(self):
        replacements = {
            "<NAME>": self.fullname,
            "<INSTRUCTOR-NAME>": self.instructor_name,
            "<KEY>": self.key,
            "<COURSE-NAME>": self.course_name,
        }

        if not os.path.exists(self.certificates_folder_path):
            os.makedirs(self.certificates_folder_path)

        command = [
            "python3",
            "-m",
            "python_pptx_text_replacer.TextReplacer",
        ]

        for attr, data in replacements.items():
            command.extend(["-m", attr, "-r", data])

        command.extend(
            ["-i", self.CERTIFICATE_TEMPLATE_PATH, "-o", self.pptx_certificate_path]
        )

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Failed to create PPTX file: {result.stderr}")

    def pptx_to_pdf(self):
        command = [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            self.certificates_folder_path,
            self.pptx_certificate_path,
        ]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Failed to convert PPTX to PDF: {result.stderr}")

        print(
            f"Converted {self.pptx_certificate_path} to PDF in {self.certificates_folder_path}"
        )

    def create(self):
        self.create_certificate_pdf()
        self.pptx_to_pdf()
        if not os.path.exists(self.certificate_path):
            raise Exception("Certificate not created")
        return self.certificate_path
