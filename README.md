# Bio-link-Tiktok
Tạo Page bio cho Tiktok không quánh sml

## Secret Scan Safety

Repo da them bo loc de tranh push nham thong tin nhay cam.

### Cai hook pre-push (chay 1 lan)

```bash
bash scripts/install-hooks.sh
```

### Quet thu cong

```bash
bash scripts/scan-secrets.sh
```

Neu script phat hien pattern nguy hiem (token/cookie/password), lenh se fail de chan push.
