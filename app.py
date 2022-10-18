import os
import re
from datetime import datetime
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
import unicodedata
from werkzeug.datastructures import FileStorage

app = Flask(__name__)
app.config["storage"] = "box/"

_windows_device_files = ("CON", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "LPT1", "LPT2", "LPT3", "PRN",)


def secure_filename(filename: str) -> str:
    r"""A modified version of `werkzeug.utils.secure_filename`"""
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("utf-8", "ignore").decode("utf-8")

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    _filter_re = re.compile(r'[^A-Za-z0-9_\u4E00-\u9FBF\u3040-\u30FF\u31F0-\u31FF.-]')
    filename = str(_filter_re.sub("", "_".join(filename.split()))).strip("._")

    if (
            os.name == "nt"
            and filename
            and filename.split(".")[0].upper() in _windows_device_files
    ):
        filename = f"_{filename}"

    return filename


def gen_file_list():
    files = os.listdir(app.config["storage"])
    result = '{"catbox":['
    for f in files:
        ff = os.curdir + '/' + app.config['storage'] + f
        result += '{' + '"f":"{f}","m":"{m}","s":{s}'.format(
            f=f,
            m=datetime.fromtimestamp(int(os.path.getmtime(ff))),
            s=os.path.getsize(ff)
        ) + '},'
    result = result[:-1] + "]}"
    return result


def accept(file: FileStorage):
    return True


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if 'form-file-input' not in request.files:
            # flash('No file part')
            return render_template("list.html", file_list=gen_file_list(), message="""
<div class="alert alert-danger alert-dismissible" role="alert">
<div>Failed uploading file.</div>
<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
</div>""")
        file = request.files['form-file-input']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            # flash('No selected file')
            return render_template("list.html", file_list=gen_file_list(), message="""
<div class="alert alert-danger alert-dismissible" role="alert">
<div>No file selected.</div>
<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
</div>""")
        if file and accept(file):
            filename = secure_filename(file.filename)
            while os.path.exists(app.config['storage'] + filename):
                ext = filename.rfind('.')
                filename = filename + "_" if ext == -1 else filename[:ext] + "_" + filename[ext:]
            file.save(os.path.join(app.config['storage'], filename))
            # return redirect(request.url)
            return render_template("list.html", file_list=gen_file_list(), message="""
<div class="alert alert-success alert-dismissible" role="alert">
<div>Success: {}</div>
<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
</div>"""
                                   .format(filename))
    return render_template("list.html", file_list=gen_file_list())


@app.route("".join(("/", app.config['storage'], "<path>")), methods=["GET"])
def download(path):
    return send_from_directory(app.config['storage'], path)


if __name__ == "__main__":
    if not os.path.isdir(app.config["storage"]):
        os.mkdir(app.config["storage"])
    app.run(host="127.0.0.1", port=25252)
