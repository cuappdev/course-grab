FROM ubuntu:18.04

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install -y curl gnupg libssl1.0.0 python-pip python

# Install SQL Server Connectors
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get -y install msodbcsql17 mssql-tools
RUN apt-get -y install unixodbc-dev unixodbc 

# Install pip dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy over source code
COPY . .

EXPOSE 5000 
CMD sh start_server.sh
# CMD python app.py
