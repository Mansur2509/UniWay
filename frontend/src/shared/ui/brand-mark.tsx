type BrandMarkProps = {
  className?: string;
};

export function BrandMark({ className }: BrandMarkProps) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      focusable="false"
      viewBox="0 0 64 64"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect fill="#18253f" height="64" width="64" />
      <path
        d="M20 16 V40 A12 12 0 0 0 32 52 A12 12 0 0 0 44 40 V16"
        fill="none"
        stroke="#f7f2e8"
        strokeLinejoin="round"
        strokeWidth="10"
      />
      <rect fill="#a41034" height="13" width="10" x="15" y="16" />
    </svg>
  );
}
