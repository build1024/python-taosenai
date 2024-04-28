FROM centos:7.9.2009 AS base

# Install/Upgrade packages
COPY CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo
RUN yum update -y && yum clean all

# ==========

FROM base AS builder
WORKDIR /opt/taosenai

# Install packages
RUN yum install -y gcc gcc-c++ patch make python3-devel file && yum clean all

# Set up Python3 env
RUN python3 -m venv venv
RUN bash -c 'source venv/bin/activate; pip install --upgrade pip && pip install requests'
RUN ln -s /lib64/libpython3.6m.so.1.0 /lib64/libpython3.6.so

# Copy and build packages
COPY openfst-1.6.9.patch setup.py .
COPY taosenai/ ./taosenai/
RUN bash -c 'source venv/bin/activate; python setup.py build'

# ==========

FROM base AS worker
WORKDIR /opt/taosenai

# Install/Upgrade packages
RUN yum install -y python3 less file which && yum clean all

# Install locale
RUN localedef -i ja_JP -f UTF-8 ja_JP.UTF-8
RUN echo 'LANG="ja_JP.UTF-8"' > /etc/locale.conf
RUN echo -e "LANG=\"ja_JP.UTF-8\"\nLANGUAGE=\"ja_JP:ja\"\nLC_ALL=\"ja_JP.UTF-8\"\nexport LANG LANGUAGE LC_ALL" >> /etc/bashrc

COPY setup.py .
COPY --from=builder /opt/taosenai/build/ ./build/
COPY --from=builder /opt/taosenai/taosenai/ ./taosenai/
RUN pip3 install requests && python3 setup.py install && rm -rf /root/.cache/pip build dist python_taosenai.egg-info taosenai setup.py 

CMD ["/bin/bash"]
