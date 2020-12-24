# Run a development server

if [ -z "$1" ]; then
    port=5000
else
    port="$1"
fi

uwsgi --socket 0.0.0.0:$port --protocol=http -w run:app --enable-threads --single-interpreter --need-app --processes 2 --master --worker-reload-mercy=1 --py-autoreload=1
