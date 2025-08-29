<script>
document.addEventListener('DOMContentLoaded', function() {
    // 模拟卡牌数据
    const cardData = [
        {
            id: 1,
            name: "火焰战士",
            type: "warrior",
            level: 3,
            attribute: "fire",
            image: "https://picsum.photos/seed/warrior1/300/300",
            url: "#card1"
        },
        {
            id: 2,
            name: "水之法师",
            type: "mage",
            level: 4,
            attribute: "water",
            image: "https://picsum.photos/seed/mage1/300/300",
            url: "#card2"
        },
        {
            id: 3,
            name: "大地弓箭手",
            type: "archer",
            level: 2,
            attribute: "earth",
            image: "https://picsum.photos/seed/archer1/300/300",
            url: "#card3"
        },
        {
            id: 4,
            name: "风之治疗师",
            type: "healer",
            level: 5,
            attribute: "air",
            image: "https://picsum.photos/seed/healer1/300/300",
            url: "#card4"
        },
        {
            id: 5,
            name: "光明坦克",
            type: "tank",
            level: 5,
            attribute: "light",
            image: "https://picsum.photos/seed/tank1/300/300",
            url: "#card5"
        },
        {
            id: 6,
            name: "黑暗刺客",
            type: "warrior",
            level: 4,
            attribute: "dark",
            image: "https://picsum.photos/seed/warrior2/300/300",
            url: "#card6"
        },
        {
            id: 7,
            name: "火焰法师",
            type: "mage",
            level: 3,
            attribute: "fire",
            image: "https://picsum.photos/seed/mage2/300/300",
            url: "#card7"
        },
        {
            id: 8,
            name: "水之弓箭手",
            type: "archer",
            level: 2,
            attribute: "water",
            image: "https://picsum.photos/seed/archer2/300/300",
            url: "#card8"
        },
        {
            id: 9,
            name: "大地守护者",
            type: "tank",
            level: 5,
            attribute: "earth",
            image: "https://picsum.photos/seed/tank2/300/300",
            url: "#card9"
        },
        {
            id: 10,
            name: "风之信使",
            type: "healer",
            level: 1,
            attribute: "air",
            image: "https://picsum.photos/seed/healer2/300/300",
            url: "#card10"
        },
        {
            id: 11,
            name: "光明使者",
            type: "mage",
            level: 4,
            attribute: "light",
            image: "https://picsum.photos/seed/mage3/300/300",
            url: "#card11"
        },
        {
            id: 12,
            name: "黑暗巫师",
            type: "mage",
            level: 5,
            attribute: "dark",
            image: "https://picsum.photos/seed/mage4/300/300",
            url: "#card12"
        }
    ];

    // 全局变量
    let currentPage = 1;
    const cardsPerPage = 6;
    let filteredCards = [...cardData];

    // DOM 元素
    const cardContainer = document.getElementById('card-container');
    const pageNumbersContainer = document.getElementById('page-numbers');
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    const levelFilter = document.getElementById('level-filter');
    const typeFilter = document.getElementById('type-filter');
    const attributeFilter = document.getElementById('attribute-filter');

    // 初始化页面
    renderCards();
    renderPagination();

    // 事件监听器
    prevPageBtn.addEventListener('click', goToPrevPage);
    nextPageBtn.addEventListener('click', goToNextPage);
    levelFilter.addEventListener('change', applyFilters);
    typeFilter.addEventListener('change', applyFilters);
    attributeFilter.addEventListener('change', applyFilters);

    // 渲染卡牌
    function renderCards() {
        cardContainer.innerHTML = '';

        const startIndex = (currentPage - 1) * cardsPerPage;
        const endIndex = startIndex + cardsPerPage;
        const currentCards = filteredCards.slice(startIndex, endIndex);

        if (currentCards.length === 0) {
            cardContainer.innerHTML = '<p class="no-cards">没有找到符合条件的卡牌</p>';
            return;
        }

        currentCards.forEach(card => {
            const cardElement = document.createElement('div');
            cardElement.className = 'card';
            cardElement.innerHTML = `
                <div class="card-image">
                    <img src="${card.image}" alt="${card.name}">
                    <div class="card-level">${card.level}</div>
                    <div class="card-attribute attribute-${card.attribute}"></div>
                </div>
                <div class="card-info">
                    <h3 class="card-name">${card.name}</h3>
                    <span class="card-type">${getTypeName(card.type)}</span>
                </div>
            `;

            cardElement.addEventListener('click', () => {
                window.location.href = card.url;
            });

            cardContainer.appendChild(cardElement);
        });
    }

    // 渲染分页
    function renderPagination() {
        pageNumbersContainer.innerHTML = '';

        const totalPages = Math.ceil(filteredCards.length / cardsPerPage);

        // 更新按钮状态
        prevPageBtn.disabled = currentPage === 1;
        nextPageBtn.disabled = currentPage === totalPages || totalPages === 0;

        // 只显示当前页附近的页码
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || Math.abs(i - currentPage) <= 1) {
                const pageNumber = document.createElement('div');
                pageNumber.className = `page-number ${i === currentPage ? 'active' : ''}`;
                pageNumber.textContent = i;
                pageNumber.addEventListener('click', () => goToPage(i));
                pageNumbersContainer.appendChild(pageNumber);
            } else if (Math.abs(i - currentPage) === 2) {
                // 添加省略号
                const ellipsis = document.createElement('div');
                ellipsis.className = 'page-number ellipsis';
                ellipsis.textContent = '...';
                ellipsis.style.pointerEvents = 'none';
                pageNumbersContainer.appendChild(ellipsis);
            }
        }
    }

    // 页面导航
    function goToPage(page) {
        currentPage = page;
        renderCards();
        renderPagination();
        scrollToTop();
    }

    function goToPrevPage() {
        if (currentPage > 1) {
            goToPage(currentPage - 1);
        }
    }

    function goToNextPage() {
        const totalPages = Math.ceil(filteredCards.length / cardsPerPage);
        if (currentPage < totalPages) {
            goToPage(currentPage + 1);
        }
    }

    // 应用筛选条件
    function applyFilters() {
        const level = levelFilter.value;
        const type = typeFilter.value;
        const attribute = attributeFilter.value;

        filteredCards = cardData.filter(card => {
            const levelMatch = level === 'all' || card.level.toString() === level;
            const typeMatch = type === 'all' || card.type === type;
            const attributeMatch = attribute === 'all' || card.attribute === attribute;

            return levelMatch && typeMatch && attributeMatch;
        });

        // 重置到第一页
        currentPage = 1;
        renderCards();
        renderPagination();
    }

    // 辅助函数：获取类型的显示名称
    function getTypeName(type) {
        const typeMap = {
            'warrior': '战士',
            'mage': '法师',
            'archer': '弓箭手',
            'healer': '治疗师',
            'tank': '坦克'
        };
        return typeMap[type] || type;
    }

    // 滚动到顶部
    function scrollToTop() {
        const catalog = document.getElementById('card-catalog');
        catalog.scrollIntoView({ behavior: 'smooth' });
    }
});
</script>