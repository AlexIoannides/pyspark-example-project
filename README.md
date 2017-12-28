# PySpark Template Project
This document is designed to be read in parallel with the `pyspark_template_project` repo on [TFS] and together constitute a 'best practices' template for writing a simple ETL job using Apache Spark and its Python ('PySpark') APIs. The project has been configured using the PyCharm IDE, which is available to download for free [here][pycharm], although this is by no means necessary. What one gains from PyCharm, is the ability to configure Python virtual environments and run configurations through a GUI, on top of all the usual code assistance (intellisense, etc), that one takes for granted with most modern IDEs.

## Project Structure
The basic project structure is as follows:

```bash
root/
 |-- dependencies/
 |   |-- logging.py
 |   tests/
 |   |-- test_etl_job.py
 |   etl_job.py
 |   build_dependencies.sh
```

The main file containing the ETL job (and which will be sent to the Spark cluster), is `etl_job.py`. Additional modules that support this job can be kept in the `dependencies/` folder (more on this later), unit test modules are kept in the `tests/` folder and a bash script for building the dependencies into a zip-file to be sent to the cluster, is also included.

## Coding Standards
Wherever possible we follow the [official Python Style Guide][PEP8], [official documentation guidelines][PEP257] and attempt to live-up to [Python's coding philosphy][PEP20]. Although these guidelines are relatively flexible we make a specific choice of style when it comes to working with the Spark API. As Spark is written in Scala - a language that embraces a functional programming paradigm by construction - and because the Python Spark APIs are nothing more than a thin wrapper around the underlying Scala APIs, we have chosen to adopt a Scala-esque style when it comes to method-chaining - e.g.,

```python
data_transformed = data_original \
    .select(['id', 'name', 'age', 'group']) \
    .groupBy('age') \
    .agg(avg('age').alias('average_age'))
```

is deemed acceptable. This is made possible, because the Python APIs ape the underlying Scala API, which passes-by-value and uses immutable types in a bid to maintain referential transparency of all function (and method) calls. Additional information on writing good Python code can be found in the [Hitchhiker's Guide to Python][hhg2py_code] and by using the [requests package][requests] as a reference project.

## Testing
We are currently making use of the `unittest` package from the [Python Standard Library][pystdlib] for writing unit tests. In order to test with Spark, we are using the `pyspark` Python package, which is bundled with the Spark JARs required to programmatically start-up and tear-down a local Spark instance, on a per-unit test basis. Note, that is an alternative way of developing with Spark as opposed to using the PySpark shell or `spark-submit`, etc.   

## Dependencies
If an ETL script has dependencies on packages other than those in the [Python Standard Library][pystdlib], then those packages must be available on each node of the cluster for the ETL job to work (unless the dependencies are only going to be accessed by the driver program on the master node). There are two ways to achieve this:

1. deploy and install the required packages on each node; or,
2. bundle all dependencies as a zip file and submit them to the cluster using the `--py-files` option with `spark-submit`.

We favour the latter option as it is more practical and flexible than the former. Consequently, we provide a bash script for automating this build process - `build_dependencies.sh`. This script is to be used as part of the following workflow for managing dependencies:

1. create a virtual Python environment in the project's root directory, that references the version of Python that the Spark cluster has been configured to use  - i.e. the same as that set for `PYSPARK_PYTHON` in `spark-env.sh` . This will be used to isolate the dependencies required for this project and can be done manually using the `virtualenv` package as described [here][hhg2py_venv], or through PyCharm by going to: Preferences -> Project -> Project Interpreter -> Create VirtualEnv, and then using the GUI to install the required packages (of which `pyspark` should be included by default to allow unit tests and intelli-sense to work).
2. run `./build_dependencies.sh dependencies_folder virtualenv_folder` in order: 
    1. to download (to a new and temporary directory) all packages installed to the virtual environment (with the exception of `pyspark` to avoid conflicts with the version on the cluster)
    2. remove unnecessary metadata to leave only the code modules;
    3. compress them into a zip; and finally, 
    4. add any custom code modules to the zip archive, which were written for this project or others like it. 

This workflow is analogous to that used to build Spark applications in Scala, which involves creating a single 'uber JAR' that includes all dependencies in one file. To be automatically copied to all nodes of the cluster.  

## Executing Jobs
For the time being all ETL jobs will be executed using `spark-submit`, which is found in `$SPARK_HOME/bin`. There are many options that can be specified, the full list of which can be found [here][spark-submit]. For the purposes of running this template project locally, the following is required,

```bash
$SPARK_HOME/bin/spark-submit \
    --master local[*] \
    --py-files dependencies.zip \
    etl_job.py 21
```

Where we assume that Spark has been downloaded locally and configured for use with Python3.


<!-- REFERENCES -->
[TFS]: https://tfs.perfectchannel.com/tfs/PerfectChannel/Perfect%20Analytics/_git/Science.PySparkTemplateProject
[pycharm]: https://www.jetbrains.com/pycharm/
[PEP8]: http://pep8.org
[PEP20]: https://www.python.org/dev/peps/pep-0020/   
[PEP257]: https://www.python.org/dev/peps/pep-0257/
[pystdlib]: https://docs.python.org/3.6/py-modindex.html
[hhg2py_code]: http://docs.python-guide.org/en/latest/#writing-great-python-code
[hhg2py_venv]: http://docs.python-guide.org/en/latest/dev/virtualenvs/
[requests]: https://github.com/requests/requests
[spark-submit]: http://spark.apache.org/docs/latest/submitting-applications.html