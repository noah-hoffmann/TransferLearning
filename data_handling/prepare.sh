for file in split_data/*.pickle.gz
do
  prepare --source-dir . --target-dir prepared &
done
for file in split_data/val/*.pickle.gz
do
  prepare --source-dir . --target-dir prepared/val &
done
for file in split_data/test/*.pickle.gz
do
  prepare --source-dir . --target-dir prepared/test &
done