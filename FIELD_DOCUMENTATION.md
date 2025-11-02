# CRM Agent Field Documentation

## Updated Field Structure (30 Fields)

### **Core Customer Information**
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `purchased` | String/null | Did the customer make a purchase? | "Yes", "No", null |
| `salesperson_name` | String/null | Name of the salesperson handling the customer | "John Smith" |
| `contact_number` | String/null | Customer's phone number | "+91-9876543210" |

### **Product Details**
| Field | Type | Description | Valid Values |
|-------|------|-------------|--------------|
| `item_type` | Enum/null | Type of jewelry item | "Bangle", "Chain", "Bracelet", "Necklace", "Earring", "Ring", "Pendant Set", "Stud", "Locket", "Hand Chain", "Nose Pin", "Mangal Sutra", "Thali", "Band Ring", null |
| `metal_type` | Enum/null | Gold purity or material type | "22K", "18K", "24K", "Diamond", "Other", null |
| `design_type`  | Enum/null | Specific design or style | "Coins / Bars", "Daily Wear", "Custom Order", "Bridal jewellery", "Kids Jewellery", "Men's Jewellery", "Temple", "Antique", "Turkish", "Calcutta", "Delhi", "Rajkot", "Local", "Singapore", "Bombay", "Italian", null |
| `item_category` | String/null | Category of the item | "Wedding", "Casual", "Formal", null |

### **Size & Weight Specifications**
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `required_size` | Number/null | Size customer needed | 22, 18, 12 |
| `required_weight` | Number/null | Weight customer wanted (in grams) | 5.5, 8.2 |
| `available_size` | Number/null | Size that was available in store | 20, 16 |
| `available_weight` | Number/null | Weight that was available | 4.8, 7.5 |

### **Pricing Information**
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `asked_price` | Number/null | Price customer asked for | 25000, 45000 |
| `given_price` | Number/null | Price offered by store | 23000, 42000 |

### **Non-Purchase Reasons (Yes/No/Null)**
| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `reason_price` | String/null | Was price the reason for not buying? | "Yes", "No", null |
| `reason_size` | String/null | Was size the reason for not buying? | "Yes", "No", null |
| `reason_weight` | String/null | Was weight the reason for not buying? | "Yes", "No", null |
| `reason_zeromaking` | String/null | Was zero making charge the reason? | "Yes", "No", null |
| `reason_design_outofstock` | String/null | Was known design out of stock the reason? | "Yes", "No", null |
| `reason_design_new` | String/null | Did customer request a new/custom design not in catalog? | "Yes", "No", null |

### **Customer Behavior & Experience**
| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `customer_intent` | String/null | Customer's shopping intention | "Just Looking", "Serious Buyer", "Price Checking", "Return Customer", null |
| `is_previous_cust` | String/null | Is customer existing POS customer? | "Yes", "No", null |
| `type_of_customer` | String/null | Type of customer | "tourist", "resident", "none", null |
| `M_Source` | String/null | Marketing source/channel | "walkin", "Social Media", "Social Groups", "Whatsup Groups", "Corporates", "Residential Cmty", "Local Cmty", "HNTW", "Hotels", "Tourism Companies", "Tour Drivers", "Other Tours Assctd cmpy", "DGJG", "Product Launch", "Other", "none", null |
| `M_source_Tag` | String/null | Marketing source tag (free text mentioned in audio) | string or null |
| `design_preference` | String/null | Customer's reaction to design | "Liked", "Disliked", "Neutral", null |
| `store_impression` | String/null | Customer's impression of store | "Good", "Poor", "Neutral", null |
| `customer_mood` | String/null | Customer's emotional state | "Happy", "Frustrated", "Neutral", "Disappointed", null |
| `customer_support` | String/null | Quality of customer support received | "Excellent", "Good", "Average", "Poor", null |
| `purchase_satisfaction` | String/null | Customer satisfaction with purchase | "Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", null |
| `waiting_time` | String/null | Customer's perception of waiting time | "Very Fast", "Fast", "Average", "Slow", "Very Slow", null |

### **Additional Data**
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `original_text` | String | Complete transcript of the conversation | "Customer wanted a 22K gold ring..." |
| `image_url` | String/null | URL or path to uploaded image | "/uploads/image123.jpg" |
| `image_description` | String/null | Description of the image content | "Customer showing preferred design" |

## **Field Usage Examples**

### **Complete Record Example:**
```json
{
  "salesperson_name": "Priya Sharma",
  "item_type": "Ring",
  "metal_type": "22K",
  "design_type": "Turkish",
  "item_category": "Wedding",
  "reason_price": "No",
  "reason_size": "Yes",
  "reason_weight": "No",
  "reason_zeromaking": "No",
  "reason_itemunavailable": "No",
  "required_size": 22,
  "required_weight": 5.5,
  "available_size": 20,
  "available_weight": 4.8,
  "asked_price": 25000,
  "given_price": 23000,
  "customer_intent": "Serious Buyer",
  "is_previous_cust": "No",
  "type_of_customer": "resident",
  "M_Source": "Social Media",
  "M_source_Tag": null,
  "design_preference": "Liked",
  "store_impression": "Good",
  "customer_mood": "Frustrated",
  "customer_support": "Good",
  "purchase_satisfaction": null,
  "waiting_time": "Average",
  "original_text": "Customer wanted a 22K gold ring in Turkey design, size 22, but we only had size 20 available. Price was acceptable."
  "contact_number": "+91-9876543210",
  "image_url": "/uploads/customer_preference.jpg",
  "image_description": "Customer showing preferred ring design from catalog"
}
```

### **Minimal Record Example:**
```json
{
  "salesperson_name": null,
  "item_type": "Necklace",
  "metal_type": "18K",
  "design_type": null,
  "item_category": null,
  "reason_price": "Yes",
  "reason_size": null,
  "reason_weight": null,
  "reason_zeromaking": null,
  "reason_itemunavailable": null,
  "required_size": null,
  "required_weight": null,
  "available_size": null,
  "available_weight": null,
  "asked_price": null,
  "given_price": null,
  "customer_intent": "Serious Buyer",
  "is_previous_cust": null,
  "type_of_customer": "tourist",
  "M_Source": "walkin",
  "M_source_Tag": "Tourist group from hotel",
  "design_preference": "Liked",
  "store_impression": "Good",
  "customer_mood": "Frustrated",
  "customer_support": "Good",
  "purchase_satisfaction": null,
  "waiting_time": "Average",
  "original_text": "Customer liked the necklace but found it too expensive.",
  "contact_number": null,
  "image_url": null,
  "image_description": null
}
```

## **Business Intelligence Queries**

### **Common Analytics Queries:**
1. **Size Issues**: `{"reason_size": "Yes"}` - Find customers who didn't buy due to size
2. **Price Sensitivity**: `{"reason_price": "Yes"}` - Find price-sensitive customers
3. **Design Preferences**: `{"design_type": {"$ne": null}}` - Popular designs
4. **Metal Preferences**: `{"metal_type": "22K"}` - Most requested gold purity
5. **Contact Follow-up**: `{"contact_number": {"$ne": null}}` - Customers to follow up
6. **Customer Intent**: `{"customer_intent": "Serious Buyer"}` - Serious buyers vs browsers
7. **Design Satisfaction**: `{"design_preference": "Liked"}` - Customers who liked designs
8. **Store Experience**: `{"store_impression": "Poor"}` - Customers with poor store experience
9. **Customer Mood**: `{"customer_mood": "Frustrated"}` - Frustrated customers needing attention
10. **Happy Customers**: `{"customer_mood": "Happy"}` - Satisfied customers for testimonials
11. **Purchase Analysis**: `{"purchased": "Yes"}` - All successful purchases
12. **Non-Purchases**: `{"purchased": "No"}` - All failed purchases
13. **Customer Support**: `{"customer_support": "Excellent"}` - Best service experiences
14. **Purchase Satisfaction**: `{"purchase_satisfaction": "Very Satisfied"}` - Highly satisfied buyers
15. **Waiting Time Issues**: `{"waiting_time": "Very Slow"}` - Customers who waited too long

## **Image Support**

### **How Images Work:**
1. **Upload**: Customer/salesperson uploads image alongside audio
2. **Processing**: Image metadata is captured
3. **Storage**: Image URL and description stored in database
4. **Analysis**: AI can analyze image content for additional insights

### **Image Use Cases:**
- Customer showing preferred designs
- Photos of items they liked
- Size reference images
- Price comparison images
- Custom design requests
