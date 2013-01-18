cp head.html $1/ani.html

cd $1
i=0
for f in *.png; do
    echo "<img id=\"pic$i\" src=\"$f\"/>" >> ani.html
    i=$((i+1))
done
echo "</body></html>" >> ani.html
