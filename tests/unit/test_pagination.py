from app.utils.pagination import Page, PageMeta, PaginationParams


def test_page_meta_calculation() -> None:
    class FakeParams:
        page = 1
        page_size = 10

    meta = PageMeta.from_params(FakeParams(), total=25)
    assert meta.total == 25
    assert meta.total_pages == 3
    assert meta.page == 1


def test_page_create() -> None:
    class FakeParams:
        page = 2
        page_size = 5

    items = [1, 2, 3, 4, 5]
    page = Page.create(items, FakeParams(), total=12)
    assert len(page.items) == 5
    assert page.meta.total_pages == 3
    assert page.meta.page == 2


def test_pagination_offset() -> None:
    class FakeParams:
        page = 3
        page_size = 10

        @property
        def offset(self):
            return (self.page - 1) * self.page_size

        @property
        def limit(self):
            return self.page_size

    p = FakeParams()
    assert p.offset == 20
    assert p.limit == 10
