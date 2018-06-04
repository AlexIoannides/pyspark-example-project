#!/usr/bin/env bash

if [ -z "$1" ]
then
    echo "ERROR - name of dependencies module not supplied."
elif [ -z "$2" ]
then
    echo "ERROR - name of Python virtual environment not supplied."
else
    # check if directories exist
    if ! [ -d $1 ]
    then
        echo "ERROR - /${1} does not exist"
        exit 1
    fi

    if ! [ -d $2 ]
    then
        echo "ERROR - /${2} does not exist"
        exit 1
    fi

    # assemble list of dependencies
    ./${2}/bin/pip3 freeze > requirements.txt

    # check to see if requirements.txt is empty
    if ! [ -s requirements.txt ]
    then
        echo "requirements.txt is empty"
        exit 1
    fi

    # remove pyspark from list of packages as this exists on Spark cluster and
    # will likely lead to conflicts
    sed -i '' '/pyspark/d' requirements.txt
    sed -i '' '/py4j/d' requirements.txt

    # install packages to a temporary directory and zip it
    ./${2}/bin/pip3 install -r requirements.txt --target ./packages

    if [ "$(ls -A packages)" ]
    then
        cd packages
        find . -name "*.pyc" -delete
        find . -name "*.egg-info" | xargs rm -rf
        find . -name "*.dist-info" | xargs rm -rf
        zip -9mrv dependencies.zip .
        mv dependencies.zip ..
        cd ..
        rm -rf packages
    fi

    # add modules from this project that need to be shipped to Spark
    zip -ru9 dependencies.zip $1
fi
