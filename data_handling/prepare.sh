path=$1;

if [ ! -d "$path"/prepared ]
  then
    mkdir "$path"/prepared
fi

for file in "$path"/split/*.pickle.gz
do
  prepare --source-dir . --target-dir "$path"/prepared --file "$file" &
done

if [ ! -d "$path"/prepared/val ]
  then
    mkdir "$path"/prepared/val
fi

for file in "$path"/split/val/*.pickle.gz
do
  prepare --source-dir . --target-dir "$path"/prepared/val --file "$file" &
done

if [ ! -d "$path"/prepared/test ]
  then
    mkdir "$path"/prepared/test
fi

for file in "$path"/split/test/*.pickle.gz
do
  prepare --source-dir . --target-dir "$path"/prepared/test --file "$file" &
done