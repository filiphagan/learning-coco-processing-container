# syntax=docker/dockerfile:1.4
FROM python:3.10.4-slim

WORKDIR /code

RUN apt update -y && apt install -y build-essential && apt install -y wget
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --upgrade wheel

RUN wget https://files.pythonhosted.org/packages/ab/94/2fc54cc791846812318080a4f86f9afcf661891163779684d1dd1fe018f9/numpy-1.21.4-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
RUN wget https://files.pythonhosted.org/packages/73/80/92054f76660e1b65f84de36d42385429c4db1837e5be579615be07955699/pandas-1.3.4-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
RUN pip install numpy-1.21.4-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
RUN pip install pandas-1.3.4-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

COPY main.py requirements.txt .
RUN pip install -r requirements.txt

