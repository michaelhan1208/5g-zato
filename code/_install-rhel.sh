#!/bin/bash

CURDIR="${BASH_SOURCE[0]}";RL="readlink";([[ `uname -s`=='Darwin' ]] || RL="$RL -f")
while([ -h "${CURDIR}" ]) do CURDIR=`$RL "${CURDIR}"`; done
N="/dev/null";pushd .>$N;cd `dirname ${CURDIR}`>$N;CURDIR=`pwd`;popd>$N

# Python version to use needs to be provided by our caller
PY_BINARY=$1
INSTALL_PYTHON=${2:-y}
echo "*** Zato RHEL/CentOS installation using $PY_BINARY ***"

INSTALL_CMD="yum"

if [ "$(type -p dnf)" ]
then
    INSTALL_CMD="dnf"
    sudo ${INSTALL_CMD} update -y

    if [ ! "$(type -p lsb_release)" ]
    then
        sudo ${INSTALL_CMD} install -y redhat-lsb-core
    fi
fi

if [[ "$INSTALL_PYTHON" == "y" ]]; then
    PYTHON_DEPENDENCIES="python3-devel"
fi

if [[ "$(lsb_release -sir)" =~ '^CentOS.8\.' ]]
then
    [[ "$INSTALL_PYTHON" == "y" ]] && sudo ${INSTALL_CMD} install -y python3
    sudo ${INSTALL_CMD} -y groupinstall development
    sudo ${INSTALL_CMD} install -y 'dnf-command(config-manager)'
    sudo ${INSTALL_CMD} config-manager --set-enabled "$(sudo dnf repolist all|grep PowerTools|awk '{print $1}')"
fi

sudo ${INSTALL_CMD} install -y \
    bzip2 bzip2-devel curl cyrus-sasl-devel gcc-c++ git haproxy \
    keyutils-libs-devel libev libev-devel libevent-devel libffi libffi-devel \
    libxml2-devel libxslt-devel libyaml-devel openldap-devel openssl \
    openssl-devel patch postgresql-devel suitesparse swig uuid \
    uuid-devel wget ${PYTHON_DEPENDENCIES}

echo Installing virtualenv in $CURDIR
$PY_BINARY -m venv .

echo Activating virtualenv in $CURDIR
source $CURDIR/bin/activate

echo Setting up environment in $CURDIR
$CURDIR/bin/python $CURDIR/util/environment.py install

echo ⭐ Successfully installed `zato --version`
