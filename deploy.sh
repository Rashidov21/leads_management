#!/bin/bash

# CRM Leads Management - Deployment Script
# Bu skriptni serverda ishga tushiring: bash deploy.sh

echo "🚀 Deployment boshlanmoqda..."
echo "================================"

# Rangli output uchun
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Backup olish
echo -e "${YELLOW}📦 Backup olinmoqda...${NC}"
python manage.py dumpdata crm_app.Lead crm_app.FollowUp > backup_$(date +%Y%m%d_%H%M%S).json
echo -e "${GREEN}✅ Backup olindi${NC}"

# 2. Git pull
echo -e "${YELLOW}📥 Yangi kod pull qilinmoqda...${NC}"
git fetch origin
git pull origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Kod yangilandi${NC}"
else
    echo -e "${RED}❌ Git pull xatolik!${NC}"
    exit 1
fi

# 3. Virtual environment aktivlashtirish va dependencies
echo -e "${YELLOW}📦 Dependencies tekshirilmoqda...${NC}"
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "env" ]; then
    source env/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo -e "${RED}❌ Virtual environment topilmadi!${NC}"
    exit 1
fi

pip install -r requirements.txt --upgrade > /dev/null 2>&1
echo -e "${GREEN}✅ Dependencies yangilandi${NC}"

# 4. Migration
echo -e "${YELLOW}🗄️  Migration tekshirilmoqda...${NC}"
python manage.py migrate --noinput
echo -e "${GREEN}✅ Migration bajarildi${NC}"

# 5. Static files
echo -e "${YELLOW}📁 Static files collect qilinmoqda...${NC}"
python manage.py collectstatic --noinput > /dev/null 2>&1
echo -e "${GREEN}✅ Static files tayyor${NC}"

# 6. Gunicorn restart
echo -e "${YELLOW}🔄 Gunicorn restart qilinmoqda...${NC}"
if sudo systemctl restart gunicorn 2>/dev/null; then
    echo -e "${GREEN}✅ Gunicorn restart qilindi${NC}"
else
    echo -e "${YELLOW}⚠️  Gunicorn service topilmadi (qo'lda restart qiling)${NC}"
fi

# 7. Celery restart
echo -e "${YELLOW}🔄 Celery restart qilinmoqda...${NC}"
if sudo systemctl restart celery 2>/dev/null; then
    echo -e "${GREEN}✅ Celery worker restart qilindi${NC}"
else
    echo -e "${YELLOW}⚠️  Celery service topilmadi${NC}"
fi

if sudo systemctl restart celerybeat 2>/dev/null; then
    echo -e "${GREEN}✅ Celery beat restart qilindi${NC}"
else
    echo -e "${YELLOW}⚠️  Celerybeat service topilmadi${NC}"
fi

# 8. Nginx reload
echo -e "${YELLOW}🔄 Nginx reload qilinmoqda...${NC}"
if sudo nginx -t > /dev/null 2>&1; then
    sudo systemctl reload nginx
    echo -e "${GREEN}✅ Nginx reload qilindi${NC}"
else
    echo -e "${YELLOW}⚠️  Nginx config xatoli${NC}"
fi

echo ""
echo "================================"
echo -e "${GREEN}✅ DEPLOYMENT TUGADI!${NC}"
echo "================================"
echo ""
echo "📊 Status tekshirish:"
echo "  - Gunicorn: sudo systemctl status gunicorn"
echo "  - Celery:   sudo systemctl status celery"
echo "  - Nginx:    sudo systemctl status nginx"
echo ""
echo "🧪 Test qilish:"
echo "  python manage.py shell"
echo ""
echo "📋 Log'lar:"
echo "  - Gunicorn: sudo journalctl -u gunicorn -f"
echo "  - Celery:   sudo journalctl -u celery -f"
echo ""

