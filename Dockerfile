# syntax=docker/dockerfile:1

# Build image from this file's directory above python/server_materials with:
    # docker build -t fpga-sim-server:v1 .
# Start container running server program with:
    # docker run -p 9834:9834 fpga-sim-server:v1 
FROM ubuntu:22.04
WORKDIR /usr/bin/


# apt-get must always be run this way in Dockerfiles

# Verilator core dependencies, plus git to download it
RUN apt-get update && apt-get install -y --no-install-recommends \
    git help2man perl python3 make autoconf g++ flex bison ccache \
    libgoogle-perftools-dev numactl perl-doc \
    git


# All of these are fine if they fail. Ignore with exit 0.
# Could omit, should fail for all Ubuntu images I think, but it feels more respectful of Verilator to not
RUN apt-get update && apt-get install -y --no-install-recommends \
    libfl-dev; exit 0
RUN apt-get update && apt-get install -y --no-install-recommends \
    libfl2; exit 0
RUN apt-get update && apt-get install -y --no-install-recommends \
    zlibc zlib1g zlib1g-dev; exit 0




# Download Verilator source to /usr/bin/
WORKDIR /usr/bin/
# fix git certificate issue
RUN apt-get update && apt-get install -y --no-install-recommends --reinstall \
    ca-certificates
RUN update-ca-certificates
RUN git clone https://github.com/verilator/verilator.git

# Build it
RUN unset VERILATOR_ROOT
WORKDIR verilator
RUN git pull
RUN git tag
RUN git checkout stable

RUN autoconf
RUN ./configure 
RUN make -j `nproc`
RUN make install


# Download uv then Python
RUN apt-get update && apt-get install -y --no-install-recommends curl
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# Updating path wasn't working so just use absolute one for the one uv call
RUN /root/.local/bin/uv python install 3.13

WORKDIR ~
RUN mkdir fpga-sim
WORKDIR ./fpga-sim


COPY python/server__manager.py python/gui__states.py python/shared__util.py \
    server_materials/Makefile server_materials/Makefile_obj \
    server_materials/simulator_driver.cpp .

# ADD ../python/server__manager.py ../python/gui__states ../python/shared__util .
# ADD ../server_materials/Makefile ../server_materials/Makefile_obj.mak ../server_materials/simulator_driver.cpp .

# COPY . .

EXPOSE 9834

# Dockerfile wizard set these
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

CMD ["/root/.local/bin/python3.13", "./server__manager.py"]