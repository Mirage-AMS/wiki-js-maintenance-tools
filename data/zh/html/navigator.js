<script>
document.addEventListener('DOMContentLoaded', function() {
    // 全局变量
    let currentPage = 1;
    const cardsPerPage = 6;
    let cardData = [];
    let filteredCards = [];

    // DOM 元素
    const cardContainer = document.getElementById('card-container');
    const pageNumbersContainer = document.getElementById('page-numbers');
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    const levelFilter = document.getElementById('level-filter');
    const typeFilter = document.getElementById('type-filter');
    const attributeFilter = document.getElementById('attribute-filter');

    // 从本地JSON文件加载卡牌数据
    loadCardData();

    // 事件监听器
    prevPageBtn.addEventListener('click', goToPrevPage);
    nextPageBtn.addEventListener('click', goToNextPage);
    levelFilter.addEventListener('change', applyFilters);
    typeFilter.addEventListener('change', applyFilters);
    attributeFilter.addEventListener('change', applyFilters);

    // 从JSON文件加载数据
    function loadCardData() {
        // 显示加载状态
        cardContainer.innerHTML = '<p class="loading">加载卡牌数据中...</p>';
        
        // 从本地JSON文件获取数据
        fetch('/assets/card.json')
            .then(response => {
                if (!response.ok) {
                    throw new Error('网络响应不正常');
                }
                return response.json();
            })
            .then(data => {
                cardData = data;
                filteredCards = [...cardData];
                renderCards();
                renderPagination();
            })
            .catch(error => {
                console.error('加载数据时出错:', error);
                cardContainer.innerHTML = '<p class="error">加载卡牌数据失败，请稍后重试</p>';
            });
    }

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