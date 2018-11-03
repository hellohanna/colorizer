from model import connect_to_db, db, User, Photo, Dataset
from flask import Flask
from resize import unzip_and_prepare
import time
import subprocess
import os
import sys
import traceback

PIX2PIX_PATH = os.environ.get('PIX2PIX_PATH', 'pix2pix')
UPLOAD_FOLDER = 'uploads'
app = Flask(__name__)

def do_work(dataset):
    """"""
    dataset_id = dataset.dataset_id
    dataset.state = Dataset.TRAINING_STARTED
    db.session.commit()

    print('Training dataset {} {}'.format(dataset.dataset_id, dataset.name))

    path_to_zip_file = os.path.abspath(os.path.join(
        UPLOAD_FOLDER, dataset.dataset_filename))

    unzip_and_prepare(path_to_zip_file, dataset_id)

    dataset_path = os.path.join(
        PIX2PIX_PATH, 'datasets', 'dataset_{}'.format(dataset_id)
    )
    model_name = 'model_{}'.format(dataset_id)

    completed = subprocess.run([
        'bash', '-c', """
            cd {pwd}
            python train.py \
                --dataroot {dataset_path} \
                --name {model_name} \
                --model pix2pix \
                --direction AtoB \
                --gpu_ids -1
        """.format(
            pwd=PIX2PIX_PATH,
            dataset_path=dataset_path,
            model_name=model_name,
        )], check=True)

    dataset.state = Dataset.TRAINING_COMPLETED
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    while True:
        try:
            time.sleep(2)
            dataset = Dataset.query.filter(
                Dataset.state == Dataset.TRAINING_REQUESTED
            ).first()
            if dataset:
                do_work(dataset)
        except:
            print("Exception while selecting or doing work:")
            print("-" * 60)
            traceback.print_exc(file=sys.stdout)
            print("-" * 60)
