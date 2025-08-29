<script>
document.addEventListener('DOMContentLoaded', function() {
    // 全局变量
    let currentPage = 1;
    const cardsPerPage = 8;
    let cardData = [];
    let filteredCards = [];
    let filterOptions = {
        levels: new Set(),
        types: new Set(),
        attributes: new Set()
    };
    let allFilterValues = {
        levels: new Set(),
        types: new Set(),
        attributes: new Set()
    };

    // DOM 元素
    const cardContainer = document.getElementById('card-container');
    const pageNumbersContainer = document.getElementById('page-numbers');
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    const filterToggle = document.getElementById('filter-toggle');
    const filtersContainer = document.getElementById('filters-container');
    const filterGroups = document.querySelector('.filter-groups');
    const clearFiltersBtn = document.getElementById('clear-filters');
    const filterCount = document.getElementById('filter-count');

    // 从本地JSON文件加载卡牌数据
    loadCardData();

    // 事件监听器
    prevPageBtn.addEventListener('click', goToPrevPage);
    nextPageBtn.addEventListener('click', goToNextPage);
    filterToggle.addEventListener('click', toggleFilters);
    clearFiltersBtn.addEventListener('click', clearAllFilters);

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
                extractFilterValues();
                renderFilterOptions();
                renderCards();
                renderPagination();
                updateFilterCount();
            })
            .catch(error => {
                console.error('加载数据时出错:', error);
                cardContainer.innerHTML = '<p class="error">加载卡牌数据失败，请稍后重试</p>';
            });
    }

    // 提取所有筛选选项值
    function extractFilterValues() {
        cardData.forEach(card => {
            allFilterValues.levels.add(card.level.toString());
            allFilterValues.types.add(card.type);
            allFilterValues.attributes.add(card.attribute);
        });
    }

    // 渲染筛选选项
    function renderFilterOptions() {
        filterGroups.innerHTML = '';

        // 等级筛选
        const levelGroup = createFilterGroup(
            '卡牌等级',
            'levels',
            Array.from(allFilterValues.levels).sort((a, b) => a - b),
            (value) => value + '级'
        );
        filterGroups.appendChild(levelGroup);

        // 类型筛选
        const typeGroup = createFilterGroup(
            '卡牌类型',
            'types',
            Array.from(allFilterValues.types),
            getTypeName
        );
        filterGroups.appendChild(typeGroup);

        // 属性筛选
        const attributeGroup = createFilterGroup(
            '卡牌属性',
            'attributes',
            Array.from(allFilterValues.attributes),
            (value) => {
                const attrMap = {
                    'fire': '火',
                    'water': '水',
                    'earth': '土',
                    'air': '风',
                    'light': '光',
                    'dark': '暗'
                };
                return attrMap[value] || value;
            }
        );
        filterGroups.appendChild(attributeGroup);
    }

    // 创建筛选组
    function createFilterGroup(label, type, values, displayFn) {
        const group = document.createElement('div');
        group.className = 'filter-group';

        const groupLabel = document.createElement('label');
        groupLabel.className = 'filter-group-label';
        groupLabel.textContent = label;
        group.appendChild(groupLabel);

        const optionsContainer = document.createElement('div');
        optionsContainer.className = 'filter-options';

        values.forEach(value => {
            const option = document.createElement('label');
            option.className = 'filter-option';
            option.innerHTML = `
                <input type="checkbox" name="${type}" value="${value}">
                <span>${displayFn(value)}</span>
            `;

            const checkbox = option.querySelector('input');
            checkbox.addEventListener('change', (e) => {
                handleFilterChange(type, e.target.value, e.target.checked);
            });

            optionsContainer.appendChild(option);
        });

        group.appendChild(optionsContainer);
        return group;
    }

    // 处理筛选变化
    function handleFilterChange(type, value, checked) {
        if (checked) {
            filterOptions[type].add(value);
        } else {
            filterOptions[type].delete(value);
        }

        applyFilters();
        updateFilterCount();
    }

    // 应用筛选条件
    function applyFilters() {
        filteredCards = cardData.filter(card => {
            const levelMatch = filterOptions.levels.size === 0 ||
                              filterOptions.levels.has(card.level.toString());
            const typeMatch = filterOptions.types.size === 0 ||
                             filterOptions.types.has(card.type);
            const attributeMatch = filterOptions.attributes.size === 0 ||
                                  filterOptions.attributes.has(card.attribute);

            return levelMatch && typeMatch && attributeMatch;
        });

        // 重置到第一页
        currentPage = 1;
        renderCards();
        renderPagination();
    }

    // 清除所有筛选
    function clearAllFilters() {
        // 重置筛选选项
        filterOptions = {
            levels: new Set(),
            types: new Set(),
            attributes: new Set()
        };

        // 取消所有勾选
        document.querySelectorAll('.filter-option input:checked').forEach(checkbox => {
            checkbox.checked = false;
        });

        applyFilters();
        updateFilterCount();
    }

    // 更新筛选计数
    function updateFilterCount() {
        const totalFilters = filterOptions.levels.size +
                            filterOptions.types.size +
                            filterOptions.attributes.size;
        filterCount.textContent = `(${totalFilters})`;
    }

    // 切换筛选面板显示/隐藏
    function toggleFilters() {
        filtersContainer.classList.toggle('filters-visible');
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