import datetime
import os
from pymediainfo import MediaInfo
from django import conf
from django.contrib.auth import get_user_model


User = get_user_model() 


def get_duration(filename):
    media_info = MediaInfo.parse(filename)
    duration_in_ms = media_info.tracks[0].duration 
    video_time = datetime.timedelta(seconds=int(duration_in_ms/ 1000))
    return video_time

class CertificatePDF:
    def __init__(self, fullname, instructor_name, key, course_name):
        self.fullname = fullname
        self.instructor_name = instructor_name
        self.key = key
        self.course_name = course_name
        self.BASE_DIR = conf.settings.BASE_DIR
        self.tmp_folder_path = os.path.join(self.BASE_DIR, "media\\tmp")
        self.pdf_path = None
        self.certificate_path = os.path.join(
            self.BASE_DIR, f"media\\certificates\\{self.key}.pdf"
        )

    def move_file_to_media(self):
        os.rename(
            self.pdf_path,
            os.path.join(self.BASE_DIR, f"media\\certificates\\{self.key}.pdf"),
        )

    def create_tmp_folder(self):
        try:
            os.mkdir(self.tmp_folder_path)
        except FileExistsError:
            print("File Already Exists!")

    def create_certificate_pdf(self):

        replacements = {
            "<NAME>": self.fullname,
            "<INSTRUCTOR-NAME>": self.instructor_name,
            "<KEY>": self.key,
            "<COURSE-NAME>": self.course_name,
        }

        CERTIFICATE_TEMPLATE_path = os.path.join(
            self.BASE_DIR, "media\CERTIFICATE-TEMPLATE.pptx"
        )
        end = f' -i {CERTIFICATE_TEMPLATE_path} -o {self.tmp_folder_path}\{replacements["<KEY>"]}.pptx'
        main_command = "python -m python_pptx_text_replacer.TextReplacer  "
        for attr, data in replacements.items():
            main_command += f' -m "{attr}" -r "{data}" '

        main_command += end
        # Execute the command
        os.system(main_command)

    def convert_pptx_pdf(self):
        command = f"pptxtopdf --input_dir {self.tmp_folder_path} --output_dir {self.tmp_folder_path}"
        os.system(command)
        self.pdf_path = os.path.join(self.tmp_folder_path, f"{self.key}.pdf")
        return self.pdf_path

    def delete_tmp_folder(self):
        for f in os.listdir(self.tmp_folder_path):
            os.remove(os.path.join(self.tmp_folder_path, f))

        os.rmdir(self.tmp_folder_path)

    def create(self):
        self.create_tmp_folder()
        self.create_certificate_pdf()
        self.convert_pptx_pdf()
        self.move_file_to_media()
        self.delete_tmp_folder()

        return self.certificate_path
