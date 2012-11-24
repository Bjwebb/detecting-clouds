cp head.html $1/index.html

cd $1
i=0
for f in *.png; do
    echo "<img id=\"pic$i\" src=\"$f\"/>" >> index.html
    i=$((i+1))
done
echo "</body></html>" >> index.html
