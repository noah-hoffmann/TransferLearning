path=$1;
for file in "$path"/split/*.pickle.gz
do
  prepare --source-dir . --target-dir "$path"/prepared --file "$file" &
done
for file in "$path"/split/val/*.pickle.gz
do
  prepare --source-dir . --target-dir "$path"/prepared/val --file "$file" &
done
for file in "$path"/split/test/*.pickle.gz
do
  prepare --source-dir . --target-dir "$path"/prepared/test --file "$file" &
done