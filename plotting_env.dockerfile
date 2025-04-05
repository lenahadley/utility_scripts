FROM mambaorg/micromamba:1-noble

# mambaorg/micromamba defaults to a non-root user. Add a "USER root" to install packages as root:
USER root

#Install ubuntu packages
RUN apt-get update && DEBIAN_FRONTEND=noninteractive \
     apt-get install -y --no-install-recommends \
     build-essential \
     git \
     curl \
     ca-certificates \     
     wget \
     pkg-config && \
     # Remove the effect of `apt-get update`
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/opt/conda/bin/:$PATH" 

#Create workdir
WORKDIR /app

# Create the environment:
RUN micromamba install --yes --name base conda-forge::pandas=2.2.2 conda-forge::numpy=1.26.4 conda-forge::matplotlib=3.9.0 conda-forge::zstandard conda-forge::pretty_html_table=0.9.16 conda-forge::seaborn=0.13.2
RUN micromamba clean --all --yes

# Activate the environment, 
ARG MAMBA_DOCKERFILE_ACTIVATE=1

RUN pip install Jinja2

ENV PATH="/opt/conda/bin/:$PATH"
