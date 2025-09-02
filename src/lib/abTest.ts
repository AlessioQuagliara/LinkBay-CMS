export function abTestHelper(req:any, testName:string, variantMap: Record<string,string>){
  // variantMap: { '1': contentA, '2': contentB } or names
  const assignments = req && req.abTests ? req.abTests : {};
  const assignedVariantId = assignments[testName];
  if (!assignedVariantId) {
    // fallback to first variant
    const first = Object.keys(variantMap)[0];
    return variantMap[first];
  }
  return variantMap[String(assignedVariantId)] || Object.values(variantMap)[0];
}
