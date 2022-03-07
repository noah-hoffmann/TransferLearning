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
for target in e-form volume
do
  echo Training target "$target"
  train-CGAT --gpus 12 --target "$target" --fea-path "$embedding_path" --epchs 390 --clr-period 130 --data-path prepared --val-path prepared/val --test-path prepared/test --batch-size 512
done
