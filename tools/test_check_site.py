# (C) PSK OG Marienheide e.V., VR/Köln 1369
"""Regression checks for privacy and project-prefix validation."""
import importlib.util
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("check_site", Path(__file__).with_name("check-site.py"))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class SiteChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)
        (self.output / "404.html").write_text('<a href="/club/">Startseite</a>')

    def page(self, text):
        (self.output / "index.html").write_text(text)

    def test_prefix_and_fragment(self):
        self.page('<h1 id="training">Training</h1><a href="/club/#training">Termine</a>')
        checker.check_site(self.output, "https://example.invalid/club/")

    def test_external_navigation_allowed(self):
        self.page('<a href="https://example.org/">Externer Link</a>')
        checker.check_site(self.output, "https://example.invalid/club/")

    def test_root_relative_asset_breaking_project_prefix(self):
        self.page('<img src="/photo.jpg" alt="Hund">')
        with self.assertRaisesRegex(ValueError, "escapes base prefix"):
            checker.check_site(self.output, "https://example.invalid/club/")

    def test_external_resources_in_multiple_attributes(self):
        for element in ['<script src="https://example.org/a.js"></script>',
                        '<img srcset="//example.org/a.jpg 2x" alt="Hund">',
                        '<link rel="preconnect" href="https://example.org/">']:
            with self.subTest(element=element):
                self.page(element)
                with self.assertRaisesRegex(ValueError, "external automatic resource"):
                    checker.check_site(self.output, "https://example.invalid/club/")

    def test_missing_fragment(self):
        self.page('<a href="#missing">Training</a>')
        with self.assertRaisesRegex(ValueError, "missing fragment"):
            checker.check_site(self.output, "https://example.invalid/club/")

    def migration_fixture(self):
        source = self.output / "source"
        (source / "data").mkdir(parents=True)
        records = []
        for number in range(27):
            route = f"/page-{number}/"
            records.append(dict(source_id=number, source_path=route,
                                outcome="migrated", target_path=route))
            target = self.output / route.lstrip("/")
            target.mkdir()
            (target / "index.html").write_text("<h1>Page</h1>")
        for name in ("impressum", "datenschutz", "downloads"):
            (self.output / name).mkdir()
            (self.output / name / "index.html").write_text("Amtsgericht Köln, VR 1369")
        pdf = b"%PDF-1.7\nReviewed PDF bytes\n"
        for name in ("reviewed.pdf", "legacy.pdf"):
            (self.output / name).write_bytes(pdf)
        (source / "reviewed.pdf").write_bytes(pdf)
        downloads = [dict(path="reviewed.pdf", url="/reviewed.pdf", legacy_urls=["/legacy.pdf"],
                          bytes=len(pdf), sha256=hashlib.sha256(pdf).hexdigest())]
        for name, value in (("migration-pages", records), ("downloads", downloads), ("migration-assets", [])):
            (source / f"data/{name}.json").write_text(json.dumps(value))
        return source

    def test_complete_migration_and_legacy_pdf(self):
        source = self.migration_fixture()
        self.assertEqual(checker.check_migration(self.output, source), [])

    def test_changed_pdf_bytes_are_rejected(self):
        source = self.migration_fixture()
        (self.output / "reviewed.pdf").write_bytes(b"%PDF-1.7\nUnreviewed PDF bytes\n")
        self.assertTrue(any("differs from reviewed PDF" in error
                            for error in checker.check_migration(self.output, source)))

    def test_missing_legacy_pdf_is_rejected(self):
        source = self.migration_fixture()
        (self.output / "legacy.pdf").unlink()
        self.assertTrue(any("Required download missing" in error
                            for error in checker.check_migration(self.output, source)))

    def test_missing_migrated_route_is_rejected(self):
        source = self.migration_fixture()
        (self.output / "page-4/index.html").unlink()
        self.assertTrue(any("Migrated source page missing" in error
                            for error in checker.check_migration(self.output, source)))

    def test_moved_page_with_legacy_route(self):
        source = self.migration_fixture()
        manifest = source / "data/migration-pages.json"
        rows = json.loads(manifest.read_text())
        rows[0]["target_path"] = "/renamed-page/"
        manifest.write_text(json.dumps(rows))
        (self.output / "renamed-page").mkdir()
        (self.output / "renamed-page/index.html").write_text("<h1>Renamed page</h1>")
        self.assertEqual(checker.check_migration(self.output, source), [])

    def test_moved_page_without_legacy_route_is_rejected(self):
        source = self.migration_fixture()
        manifest = source / "data/migration-pages.json"
        rows = json.loads(manifest.read_text())
        rows[0]["target_path"] = "/renamed-page/"
        manifest.write_text(json.dumps(rows))
        (self.output / "page-0").rename(self.output / "renamed-page")
        self.assertTrue(any("Legacy source page missing" in error
                            for error in checker.check_migration(self.output, source)))


if __name__ == "__main__":
    unittest.main()
