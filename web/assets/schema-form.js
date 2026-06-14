export function fieldsForMode(schema, mode) {
  return schema.fields.filter(
    (field) => field.stage === "PRE_LAB" || mode === "LAB_AWARE"
  );
}


export function validateFormValues(schema, mode, values) {
  const errors = {};
  for (const field of fieldsForMode(schema, mode)) {
    const value = values[field.field_id];
    if (field.required && (value === undefined || value === "" || value === null)) {
      errors[field.field_id] = "Required";
    } else if (field.type === "number" && value !== undefined && value !== "" && !Number.isFinite(Number(value))) {
      errors[field.field_id] = "Enter a number";
    }
  }
  return errors;
}


export function serializeAssessment(schema, mode, values) {
  const allowed = new Set(fieldsForMode(schema, mode).map((field) => field.field_id));
  const serialized = {};
  for (const [key, value] of Object.entries(values)) {
    if (!allowed.has(key) || value === "") continue;
    const field = schema.fields.find((item) => item.field_id === key);
    serialized[key] = field.type === "number" && value !== null ? Number(value) : value;
  }
  return { mode, values: serialized };
}
