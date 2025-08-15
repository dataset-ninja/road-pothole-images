Dataset **Road Pothole Images** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/remote/eyJsaW5rIjogInMzOi8vc3VwZXJ2aXNlbHktZGF0YXNldHMvMTY1MV9Sb2FkIFBvdGhvbGUgSW1hZ2VzL3JvYWQtcG90aG9sZS1pbWFnZXMtRGF0YXNldE5pbmphLnRhciIsICJzaWciOiAiOUFTN25NbHBENDlmdGtRTndxc3Jpb1J1aWFKOG9kR1pHaHl0YUV3YVB6RT0ifQ==?response-content-disposition=attachment%3B%20filename%3D%22road-pothole-images-DatasetNinja.tar%22)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='Road Pothole Images', dst_dir='~/dataset-ninja/')
```
Make sure not to overlook the [python code example](https://developer.supervisely.com/getting-started/python-sdk-tutorials/iterate-over-a-local-project) available on the Supervisely Developer Portal. It will give you a clear idea of how to effortlessly work with the downloaded dataset.

The data in original format can be [downloaded here](https://drive.google.com/drive/folders/1vUmCvdW3-2lMrhsMbXdMWeLcEz__Ocuy).