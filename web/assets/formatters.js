export const titleCase = (value) =>
  String(value ?? "")
    .replace(/[{}_]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());

export const percent = (value, digits = 1) =>
  Number.isFinite(Number(value)) ? `${(Number(value) * 100).toFixed(digits)}%` : "N/A";

export const number = (value, digits = 2) =>
  Number.isFinite(Number(value)) ? Number(value).toFixed(digits) : "N/A";

export const listLabels = (value) =>
  String(value || "")
    .replace(/[{}]/g, "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
