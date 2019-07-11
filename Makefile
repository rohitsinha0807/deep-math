.PHONY: gradient_job data

#################################################################################
# COMMANDS                                                                      #
#################################################################################
gradient_job:
	gradient jobs create \
	--name "lstm_test" \
	--container tensorflow/tensorflow:2.0.0a0-gpu-py3-jupyter \
	--machineType GPU+ \
	--command "/paperspace/run_script.sh" \
	--ignoreFiles "data,env"

data:
	mkdir -p data/raw/
	cd data/raw/; gsutil cp gs://mathematics-dataset/mathematics_dataset-v1.0.tar.gz .
	cd data/raw; tar -xvzf mathematics_dataset-v1.0.tar.gz
	cd data/raw; rm mathematics_dataset-v1.0.tar.gz