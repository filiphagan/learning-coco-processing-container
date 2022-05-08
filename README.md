# COCO data processing with Docker

## Description
Learning task: Data processing container transforming [COCO-formatted data](https://cocodataset.org/#format-data) to CSV.
In this example the script expects the URL to zipped archive including person_keypoints_val2017.json

Requirements: docker <br>

## Contents
- main.py
- Dockerfile
- requirements.txt
- README.md

## Execution

1) Build the docker image

```
docker build -t mlops-coco <path/to/Dockerfile>
```

2) Run the container

```
docker run --name my-coco -t -d mlops-coco
```

3) Run processing script

Parameters: <br>
--url (str): url to zipped COCO-formatted data package including person_keypoints_val2017.json<br>
--output (str): path to output csv file

```
docker exec my-coco /code/main.py --url <https://url/to/filename.zip> --output <path/filename.csv>

# Example:
docker exec my-coco python /code/main.py --url "http://images.cocodataset.org/annotations/annotations_trainval2017.zip" --output "/output/out.csv"
```
Check if the file exists in output directory
```
docker exec my-coco sh -c "cd /output; ls -l"
```