FROM ubuntu:focal-20240416 AS builder
WORKDIR /opt/taosenai

# Set apt mirror
COPY sources.list /etc/apt/sources.list

# Install packages
RUN apt update && apt install -y gcc g++ make file python3 python3-dev python3-venv && apt clean

# Set up Python3 env
RUN python3 -m venv venv
RUN bash -c 'source venv/bin/activate; pip install --upgrade pip && pip install requests'

# Copy and build packages
COPY setup.py .
COPY taosenai/ ./taosenai/
RUN bash -c 'source venv/bin/activate; python setup.py build'

# ==========

FROM ubuntu:focal-20240416 AS worker
WORKDIR /opt/taosenai

# Set apt mirror
COPY sources.list /etc/apt/sources.list

# Install/Upgrade packages
RUN apt update && apt install -y python3 python3-pip less file language-pack-ja && apt clean

# Set locale
RUN /bin/echo -e "LANG=\"ja_JP.UTF-8\"\nLANGUAGE=\"ja_JP:ja\"\nLC_ALL=\"ja_JP.UTF-8\"\nexport LANG LANGUAGE LC_ALL" >> /etc/bash.bashrc

COPY setup.py .
COPY --from=builder /opt/taosenai/build/ ./build/
COPY --from=builder /opt/taosenai/taosenai/ ./taosenai/
RUN pip install requests && python3 setup.py install && rm -rf /root/.cache/pip build dist python_taosenai.egg-info taosenai setup.py

CMD ["/bin/bash"]
