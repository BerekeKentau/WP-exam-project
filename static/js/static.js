function scrollToCategory(categoryId) {
    const section = document.getElementById(categoryId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}
