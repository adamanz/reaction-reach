#!/usr/bin/env node

/**
 * Extract Adam Anzuoni Phone Number via API
 * Based on the UI showing +14015758192 for Adam Anzuoni at FUNDWELL
 */

const axios = require('axios');
const fs = require('fs');

// Apollo API configuration
const APOLLO_API_KEY = process.env.APOLLO_API_KEY;
const APOLLO_BASE_URL = 'https://api.apollo.io/v1';

// Alternative APIs to try
const APIs = {
    apollo: {
        name: 'Apollo.io',
        searchEndpoint: '/people/search',
        enrichEndpoint: '/people/enrich'
    },
    clearbit: {
        name: 'Clearbit',
        baseUrl: 'https://person.clearbit.com/v2'
    },
    hunter: {
        name: 'Hunter.io', 
        baseUrl: 'https://api.hunter.io/v2'
    }
};

async function searchAdamAnzuoniApollo() {
    try {
        console.log('🔍 Searching for Adam Anzuoni via Apollo API...');
        
        if (!APOLLO_API_KEY) {
            console.log('❌ APOLLO_API_KEY not set, skipping Apollo search');
            return null;
        }

        const searchPayload = {
            api_key: APOLLO_API_KEY,
            person_titles: ['Chief Technology Officer', 'CTO'],
            organization_names: ['FUNDWELL', 'Fundwell'],
            q_keywords: 'Adam Anzuoni',
            per_page: 10
        };

        const response = await axios.post(`${APOLLO_BASE_URL}/people/search`, searchPayload);
        
        if (response.data && response.data.people) {
            console.log(`✅ Found ${response.data.people.length} people via Apollo`);
            
            const adamProfile = response.data.people.find(person => 
                person.first_name?.toLowerCase().includes('adam') && 
                person.last_name?.toLowerCase().includes('anzuoni')
            );
            
            if (adamProfile) {
                console.log('🎯 Found Adam Anzuoni profile:');
                console.log(`   Name: ${adamProfile.first_name} ${adamProfile.last_name}`);
                console.log(`   Title: ${adamProfile.title}`);
                console.log(`   Company: ${adamProfile.organization?.name}`);
                console.log(`   Phone: ${adamProfile.sanitized_phone || adamProfile.phone || 'Not available'}`);
                console.log(`   Email: ${adamProfile.email || 'Not available'}`);
                
                return {
                    source: 'Apollo',
                    name: `${adamProfile.first_name} ${adamProfile.last_name}`,
                    phone: adamProfile.sanitized_phone || adamProfile.phone,
                    email: adamProfile.email,
                    title: adamProfile.title,
                    company: adamProfile.organization?.name,
                    linkedin: adamProfile.linkedin_url
                };
            }
        }
        
        return null;
        
    } catch (error) {
        console.error('❌ Apollo API error:', error.response?.data || error.message);
        return null;
    }
}

async function enrichAdamAnzuoniApollo() {
    try {
        console.log('🔍 Enriching Adam Anzuoni via Apollo API...');
        
        if (!APOLLO_API_KEY) {
            return null;
        }

        const enrichPayload = {
            api_key: APOLLO_API_KEY,
            first_name: 'Adam',
            last_name: 'Anzuoni',
            organization_name: 'FUNDWELL',
            reveal_phone_number: true
        };

        const response = await axios.post(`${APOLLO_BASE_URL}/people/enrich`, enrichPayload);
        
        if (response.data && response.data.person) {
            const person = response.data.person;
            console.log('🎯 Enriched Adam Anzuoni profile:');
            console.log(`   Name: ${person.first_name} ${person.last_name}`);
            console.log(`   Phone: ${person.sanitized_phone || person.phone || 'Not available'}`);
            console.log(`   Email: ${person.email || 'Not available'}`);
            
            return {
                source: 'Apollo Enrich',
                name: `${person.first_name} ${person.last_name}`,
                phone: person.sanitized_phone || person.phone,
                email: person.email,
                title: person.title,
                company: person.organization?.name
            };
        }
        
        return null;
        
    } catch (error) {
        console.error('❌ Apollo Enrich error:', error.response?.data || error.message);
        return null;
    }
}

async function searchWithExa() {
    try {
        console.log('🔍 Cross-referencing with Exa API...');
        
        if (!process.env.EXA_API_KEY) {
            console.log('❌ EXA_API_KEY not set, skipping Exa search');
            return null;
        }

        const { Exa } = require('exa-js');
        const exa = new Exa(process.env.EXA_API_KEY);

        const results = await exa.searchAndContents('Adam Anzuoni FUNDWELL CTO Chief Technology Officer phone contact', {
            numResults: 5
        });

        console.log(`✅ Exa found ${results.results.length} related sources`);
        
        const phoneMatches = [];
        results.results.forEach(result => {
            if (result.text) {
                const phones = result.text.match(/(\+?1[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})/g);
                if (phones) {
                    phones.forEach(phone => {
                        if (phone.includes('401') || phone.includes('4015758192')) {
                            phoneMatches.push({
                                phone: phone,
                                source: result.title,
                                url: result.url
                            });
                        }
                    });
                }
            }
        });

        return phoneMatches.length > 0 ? phoneMatches : null;
        
    } catch (error) {
        console.error('❌ Exa search error:', error.message);
        return null;
    }
}

async function validatePhoneNumber(phone) {
    // Clean and validate the phone number
    const cleaned = phone?.replace(/[^\d+]/g, '');
    
    if (!cleaned) return null;
    
    // Check if it matches the expected format from UI
    const expectedPhone = '+14015758192';
    const cleanedExpected = expectedPhone.replace(/[^\d+]/g, '');
    
    if (cleaned === cleanedExpected || cleaned.includes('4015758192')) {
        return {
            raw: phone,
            cleaned: cleaned,
            formatted: '+1 (401) 575-8192',
            verified: true,
            matchesUI: true
        };
    }
    
    return {
        raw: phone,
        cleaned: cleaned,
        formatted: phone,
        verified: false,
        matchesUI: false
    };
}

async function main() {
    try {
        console.log('📞 Extracting Adam Anzuoni Phone Number via API');
        console.log('=' .repeat(60));
        console.log('📱 Expected from UI: +14015758192');
        console.log('🏢 Company: FUNDWELL');
        console.log('💼 Title: Chief Technology Officer');
        console.log('');

        const results = {
            expectedFromUI: '+14015758192',
            timestamp: new Date().toISOString(),
            sources: []
        };

        // Try Apollo search
        const apolloSearch = await searchAdamAnzuoniApollo();
        if (apolloSearch) {
            results.sources.push(apolloSearch);
        }

        // Try Apollo enrich
        const apolloEnrich = await enrichAdamAnzuoniApollo();
        if (apolloEnrich) {
            results.sources.push(apolloEnrich);
        }

        // Try Exa cross-reference
        const exaResults = await searchWithExa();
        if (exaResults) {
            results.sources.push({
                source: 'Exa Cross-Reference',
                matches: exaResults
            });
        }

        // Validate any found phone numbers
        const foundPhones = [];
        results.sources.forEach(source => {
            if (source.phone) {
                const validation = validatePhoneNumber(source.phone);
                foundPhones.push({
                    source: source.source,
                    phone: validation
                });
            }
        });

        results.phoneValidation = foundPhones;

        // Save results
        const outputFile = `/Users/adamanzuoni/ReactionReach/adam_anzuoni_phone_extraction_${Date.now()}.json`;
        fs.writeFileSync(outputFile, JSON.stringify(results, null, 2));

        console.log('📊 RESULTS SUMMARY:');
        console.log(`   Sources checked: ${results.sources.length}`);
        console.log(`   Phone numbers found: ${foundPhones.length}`);
        console.log(`   Results saved to: ${outputFile}`);

        if (foundPhones.length > 0) {
            console.log('\n📞 PHONE NUMBERS FOUND:');
            foundPhones.forEach((item, i) => {
                console.log(`${i+1}. Source: ${item.source}`);
                console.log(`   Phone: ${item.phone.formatted}`);
                console.log(`   Matches UI: ${item.phone.matchesUI ? '✅' : '❌'}`);
                console.log(`   Verified: ${item.phone.verified ? '✅' : '❌'}`);
            });
        } else {
            console.log('\n❌ No phone numbers found via API');
            console.log('💡 The phone number +14015758192 is visible in UI but may require:');
            console.log('   - Premium Apollo subscription for phone reveal');
            console.log('   - Special API permissions for contact data');
            console.log('   - Browser automation to extract from UI directly');
        }

        console.log('\n🎯 RECOMMENDATION:');
        console.log('Since the phone number is visible in the UI (+14015758192),');
        console.log('you may need to use browser automation or premium API access');
        console.log('to programmatically extract this contact information.');

    } catch (error) {
        console.error('💥 Fatal error:', error.message);
        process.exit(1);
    }
}

// Run if called directly
if (require.main === module) {
    main();
}

module.exports = {
    searchAdamAnzuoniApollo,
    enrichAdamAnzuoniApollo,
    validatePhoneNumber
};