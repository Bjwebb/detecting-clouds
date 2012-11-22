cat head.html

cd $1
i=0
for f in *.png; do
    echo "<img id=\"pic$i\" src=\"$f\"/>"
    i=$((i+1))
done
echo "</body></html>"
