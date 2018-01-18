# PySpark Example Project
This document is designed to be read in parallel with the code in the `pyspark-template-project` repo and together constitute what we consider to be a 'best practices' approach and template project for writing ETL jobs using Apache Spark and its Python ('PySpark') APIs. This project addresses the following topics:
- how to pass configuration parameters to a PySpark job;
- how to handle dependencies on other modules and packages;
- how to structure ETL code in such a way that it can be easily tested and debugged; and,
- what constitutes a 'meaningful' test for an ETL job.

## Getting Started
We recommend setting up a Python 3 virtual environment for your ETL project. Assuming that you have the `virtualenv` package installed into your global Python site packages repository (i.e. you have run `pip3 install virtualenv` at some point in the past), then this can be done through the bash terminal as follows,

```bash
python3 -m venv venv
```

This will create a directory, `venv/`, containing the Python 3 virtual environment. The version of Python used should be the same as the one that the Spark cluster has been configured to use  - i.e. the same as that set for `PYSPARK_PYTHON` in `$SPARK_HOME/conf/spark-env.sh`.

In order to get operational with this project it needs to be activated and PySpark has to be installed. This can be achieved with the following commands on the terminal,

```bash
source venv/bin/activate
pip3 install pyspark
```

You should now be ready to go! 

An alternative to the above, is to construct the virtual environment using the PyCharm IDE for Python, which is available to download for free [here][pycharm]. What one gains from PyCharm, is the ability to configure Python virtual environments and run configurations through a GUI, on top of all the usual code assistance (intellisense, etc), that one takes for granted with most modern IDEs. Constructing the virtual environment is as simple as by going to: Preferences -> Project -> Project Interpreter -> Create VirtualEnv, and then using the GUI to install the required packages (of which `pyspark` should be included by default to allow unit tests and intelli-sense to work as we did above). 

## Project Structure
The basic project structure is as follows:

```bash
root/
 |-- dependencies/
 |   |-- logging.py
 |   tests/
 |   |-- test_data/
 |   |-- | -- employees/
 |   |-- | -- employees_report/
 |   |-- test_etl_job.py
 |   etl_job.py
 |   etl_config.json
 |   build_dependencies.sh
```

The main Python module containing the ETL job (which will be sent to the Spark cluster), is `etl_job.py`. Any external configuration parameters required by `etl_job.py` are stored in JSON format in `etl_config.json`. Additional modules that support this job can be kept in the `dependencies/` folder (more on this later) and a bash script for building the dependencies into a zip-file to be sent to the cluster, is also included (`build_dependencies.sh`). Unit test modules are kept in the `tests/` folder and small chunks of representative input and output data are kept in `tests/test_data` folder.   

## Running the ETL job
Assuming that the `$SPARK_HOME` environment variable points to your local Spark installation folder, then the ETL job can be run from the project's root directory using the following command from the terminal,

```bash
$SPARK_HOME/bin/spark-submit \
--master local[*] \
--py-files dependencies.zip \
--files etl_config.json \
etl_job.py
```

If you have a Spark cluster in operation (either in single-executor mode locally or something larger in the cloud) and want to send the job there, then modify the `--master` option with the Spark IP - e.g. `--master spark://localhost:7077`. 

## Passing Configuration Parameters to the ETL Job
Although it is possible to pass arguments to `etl_job.py`, as you would for any generic Python module running as a 'main' program  - by specifying them after the module's filename and then parsing these command line arguments - this can get very complicated, very quickly, especially when there are lot of parameters (e.g. credentials for multiple databases, table names, SQL snippets, etc.). This also makes debugging the code from within a Python interpreter extremely awkward, as you don't have access to the command line arguments that would ordinarily be passed to the code, when calling it from the command line. 

A much more effective solution is to send Spark a separate file - e.g. using the `--files etl_config.json` flag with `spark-subit` - containing the configuration in JSON format, which can be parsed into a Python dictionary in one line of code with `json.loads(config_file_contents)`. Testing the code from within a Python interactive console session is also greatly simplified, as all one has to do to access configuration parameters for testing, is to copy and paste the contents of the file - e.g.,

```python
import json

config = json.loads("""{"steps_per_floor": 21}""")
```

For the exact details of how the configuration file is located, opened and parsed, please see the `start_spark()` function in `etl_job.py`, which also launches the Spark driver program and retrieves the Spark logger as well. 

## Coding Standards
Wherever possible we follow the [official Python Style Guide][PEP8], [official documentation guidelines][PEP257] and attempt to live-up to [Python's coding philosphy][PEP20]. Although these guidelines are relatively flexible we make a specific choice of style when it comes to working with the Spark API. As Spark is written in Scala - a language that embraces a functional programming paradigm by construction - and because the Python Spark APIs are nothing more than a thin wrapper around the underlying Scala APIs, we have chosen to adopt a Scala-esque style when it comes to method-chaining - e.g.,

```python
data_transformed = (
    data_original 
    .select(['id', 'name', 'age', 'group'])
    .groupBy('age')
    .agg(avg('age').alias('average_age')))
```

is deemed acceptable. This is made possible, because the Python APIs ape the underlying Scala API, which passes-by-value and uses immutable types in a bid to maintain referential transparency of all function (and method) calls. Additional information on writing good Python code can be found in the [Hitchhiker's Guide to Python][hhg2py_code] and by using the [requests package][requests] as a reference project.

## Structure of an ETL Job
In order to facilitate easy debugging and testing, we recommend that the 'Transformation' step be isolated from the 'Extract' and 'Load' steps, into it's own function, which takes input data arguments in the form of DataFrames and returns the transformed data as a single DataFrame. Then, the code that surrounds the use of the transformation function in the `main()` job function, is concerned with Extracting the data, passing it to the transformation function and then Loading (or writing) the results to their ultimate destination. Testing is simplified, as mock or test data can be passed to the transformation function and the results explicitly verified, which would not be possible if all of the code resided in `main()` and referenced production data sources and destinations.

More generally, transformation functions should be designed to be idempotent. This is technical way of saying that the repeated application of the transformation function should have no impact on the fundamental state of output data, until the instance when the input data changes. One of the key advantages of idempotent ETL jobs, is that they can be set to run repeatedly (e.g. by using `cron` to trigger the `spark-submit` command above, on a pre-defined schedule), rather than having to factor-in potential dependencies on other ETL jobs completing successfully.   

## Testing
We are currently making use of the `unittest` package from the [Python Standard Library][pystdlib] for writing unit tests. In order to test with Spark, we are using the `pyspark` Python package, which is bundled with the Spark JARs required to programmatically start-up and tear-down a local Spark instance, on a per-test-suite basis. Note, this is an alternative way of developing with Spark as opposed to using the PySpark shell or `spark-submit`, etc. Given that we have chosen to structure our ETL jobs in such a way as to isolate the 'Transformation' step into its own function (see above), we are free to feed it a small slice of 'real-world' production data that has been persisted locally - e.g. in `tests/test_data` or some easily accessible network directory - and check it against known results (e.g. computed manually or interactively within a Python interactive console session).

## Dependencies
If an ETL script has dependencies on packages other than those in the [Python Standard Library][pystdlib], then those packages must be made available to *every* node of the cluster for the ETL job to work (unless the dependencies are only going to be accessed by the driver program on the master node). There are two ways to achieve this:

1. deploy and install the required packages on each node; or,
2. bundle all dependencies as a zip file and submit them to the cluster using the `--py-files` option with `spark-submit`.

We favour the latter option as it is more practical and flexible than the former. Consequently, we provide a bash script for automating this build process - `build_dependencies.sh`. This script is to be used as part of the following workflow for managing dependencies:

1. as already mentioned at the beginning, make sure that you create a virtual Python environment in the project's root directory, which references the version of Python that the Spark cluster has been configured to use  - i.e. the same as that set for `PYSPARK_PYTHON` in `$SPARK_HOME/conf/spark-env.sh`. This will be used to isolate the dependencies required for this project and can be done manually using the `virtualenv` package as described above and [here][hhg2py_venv].
2. run `./build_dependencies.sh dependencies_folder virtualenv_folder` in order: 
    1. to download (to a new and temporary directory) all packages installed to the virtual environment (with the exception of `pyspark` to avoid conflicts with the version on the cluster);
    2. remove unnecessary metadata to leave only the code modules;
    3. compress them into a zip; and finally, 
    4. add any custom code modules to the zip archive, which were written for this project or others like it. 

This workflow is analogous to that used to build Spark applications in Scala, which involves creating a single 'uber JAR' that includes all dependencies in one file, to be automatically copied to all nodes of the cluster. It should be noted, that dependencies requiring C/C++ code to be compiled (e.g. numpy) cannot be handled in this way. These will have to be manually installed into the global Python site-packages on every Spark node. 


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
