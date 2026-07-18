// Single source of truth for the landing page's university-count claim.
// Verified against the live production /universities catalog (454 real
// universities at verification time); rounded down to a conservative,
// always-true "450+" so the claim stays honest even as the catalog changes
// slightly. Re-verify against production before raising this number.
export const UNIVERSITY_COUNT_DISPLAY = 450;
