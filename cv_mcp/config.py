"""Environment-backed runtime configuration."""

from pathlib import Path

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for the builder, MCP server, and artifact downloads."""

    model_config = SettingsConfigDict(
        env_prefix="CV_MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    root: Path = Field(default_factory=Path.cwd)
    profile: Path = Path("profile/career.yaml")
    applications: Path = Path("applications")
    output: Path = Path("build")
    fonts: Path | None = None
    download_base_url: str = ""
    download_signing_secret: str = ""
    build_timeout_seconds: int = Field(
        default=120,
        ge=1,
        le=3600,
        validation_alias=AliasChoices(
            "CV_MCP_BUILD_TIMEOUT", "CV_MCP_BUILD_TIMEOUT_SECONDS"
        ),
    )
    log_level: str = "INFO"

    @model_validator(mode="after")
    def resolve_paths(self) -> "Settings":
        """Resolve omitted paths relative to the configured project root."""
        root = self.root.expanduser().resolve()
        self.root = root
        self.profile = self._resolve(self.profile, root)
        self.applications = self._resolve(self.applications, root)
        self.output = self._resolve(self.output, root)
        if self.fonts:
            self.fonts = self._resolve(self.fonts, root)
        return self

    @staticmethod
    def _resolve(path: Path, root: Path) -> Path:
        path = path.expanduser()
        return path if path.is_absolute() else (root / path).resolve()

    def ensure_runtime(self) -> None:
        """Validate mounted inputs and create the writable output directory."""
        if not self.profile.is_file():
            raise RuntimeError(f"Career profile does not exist: {self.profile}")
        if not self.applications.is_dir():
            raise RuntimeError(
                f"Applications directory does not exist: {self.applications}"
            )
        self.output.mkdir(parents=True, exist_ok=True)
        if self.fonts and not self.fonts.is_dir():
            raise RuntimeError(f"Fonts directory does not exist: {self.fonts}")
