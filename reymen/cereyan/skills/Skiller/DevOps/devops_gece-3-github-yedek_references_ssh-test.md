# SSH test
ssh -T git@github.com 2>&1 | grep -q "successfully authenticated" && echo "SSH OK"