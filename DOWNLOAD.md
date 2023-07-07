Dataset **Road Pothole Images** can be downloaded in Supervisely format:

 [Download](https://assets.supervisely.com/supervisely-supervisely-assets-public/teams_storage/8/h/7u/UtiEpsAvjJiRpIPrOye6EWNplDeOPUZ70im7VwWHAYcnr24Q5EPHsfEK1o0NB9Wnb9HkY8bbdTjP5ZLzYVP1V1xcVfbOW3sZPQxQwzc4yTiqmK0A1UhLf6vBzzwD.tar)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='Road Pothole Images', dst_path='~/dtools/datasets/Road Pothole Images.tar')
```
The data in original format can be 🔗[downloaded here](https://www.kaggle.com/datasets/sovitrath/road-pothole-images-for-pothole-detection/download?datasetVersionNumber=2)