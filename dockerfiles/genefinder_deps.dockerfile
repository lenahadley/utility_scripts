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
RUN micromamba install --yes --name base bioconda::sambamba=1.0.1 bioconda::samtools=1.20 bioconda::pysamstats=1.1.2 bioconda::minimap2=2.28 bioconda::pyfaidx=0.8.1.1 conda-forge::pandas=2.2.2 conda-forge::lxml=5.2.2 conda-forge::numpy=1.26.4
RUN micromamba clean --all --yes

# Activate the environment, 
ARG MAMBA_DOCKERFILE_ACTIVATE=1
