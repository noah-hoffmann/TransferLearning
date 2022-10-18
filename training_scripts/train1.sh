embedding_path="embeddings/matscholar-embeddings.json"
for directory in "prepared" "prepared/val" "prepared/test"
do
  if [ ! -d "$directory" ]
  then
    echo "Can't find directory '$directory', please check current working directory!"
    exit 1
  fi
done
if [ ! -f "$embedding_path" ]
then
  echo "Can't find embedding file, please check current working directory!"
  exit 1
fi

# Training loop
target="e_above_hull_new"
for set_size in 0.2 0.4 0.6 0.8
do
  echo "Training set size $set_size"
  train-CGAT --gpus 12 --target "$target" --fea-path "$embedding_path" --epchs 400 --clr-period 70 --data-path prepared --val-path prepared/val --test-path prepared/test --train-percentage "$set_size"
done
