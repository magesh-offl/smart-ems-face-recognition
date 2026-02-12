
export const maskDateInput = (value: string): string => {
    // 1. Remove non-digits and limit length
    let v = value.replace(/\D/g, '').slice(0, 8);
    
    // 2. Extract parts
    let dayStr = v.slice(0, 2);
    let monthStr = v.slice(2, 4);
    let yearStr = v.slice(4, 8);
    
    // 3. Validate Day (Basic 1-31)
    if (dayStr.length === 2) {
        let d = parseInt(dayStr);
        if (d === 0) d = 1;
        if (d > 31) d = 31;
        dayStr = d.toString().padStart(2, '0');
    }
    
    // 4. Validate Month (1-12)
    if (monthStr.length === 2) {
        let m = parseInt(monthStr);
        if (m === 0) m = 1;
        if (m > 12) m = 12;
        monthStr = m.toString().padStart(2, '0');
    }
    
    // 5. Cross-Check Day against Month (and Year if valid)
    if (dayStr.length === 2 && monthStr.length === 2) {
        const d = parseInt(dayStr);
        const m = parseInt(monthStr);
        
        // Use 2024 (leap year) as default if year is incomplete
        // This ensures 29-02 is allowed while typing
        const y = yearStr.length === 4 ? parseInt(yearStr) : 2024;
        
        if (m > 0) {
            const daysInMonth = new Date(y, m, 0).getDate();
            if (d > daysInMonth) {
                dayStr = daysInMonth.toString().padStart(2, '0');
            }
        }
    }
    
    // 6. Reassemble with hyphens
    let res = dayStr;
    if (v.length >= 3) { // Started typing month (index 2)
        res += '-' + monthStr;
    }
    if (v.length >= 5) { // Started typing year (index 4)
        res += '-' + yearStr;
    }
    
    return res;
};
