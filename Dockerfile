FROM tensorflow/tensorflow:2.1.0-py3

# Copy requirements file
COPY requirements.txt requirements.txt

# Install requirements
RUN pip3 install -r requirements.txt

# Copy files
COPY server.py server.py
COPY serve_model.py serve_model.py
COPY data_proc.py data_proc.py
COPY models/ models/

# Expose port and run server
EXPOSE 5000
CMD ["python3", "server.py"]