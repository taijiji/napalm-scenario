FROM centos:7

MAINTAINER Taiji Tsuchiya

RUN yum update -y
RUN yum -y install yum-utils
RUN yum -y install https://centos7.iuscommunity.org/ius-release.rpm
RUN yum -y install epel-release

# Install Git
RUN yum -y install git
RUN git --version

# Install Python3,6 environment
RUN yum -y install python36u
RUN yum -y install python36u-pip
RUN yum -y install python36u-devel.x86_64

WORKDIR /
RUN git clone https://33d8d1dc3e41987ce41a96526417c8e50f9e64ce:x-oauth-basic@github.com/ctcamerica/chartwith.git
WORKDIR /chartwith
RUN pip3.6 install -r requirements.txt
