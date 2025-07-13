#!/usr/bin/env node

/**
 * Adam Anzuoni Contact Enrichment with Exa Websets
 * Searches for phone number and contact information
 */

const { Exa } = require('exa-js');
const fs = require('fs');

// Initialize Exa with API key from environment
const exa = new Exa(process.env.EXA_API_KEY);

async function createAdamAnzuoniEnrichment() {
    try {
        console.log('🔍 Creating Adam Anzuoni Contact Enrichment Webset...');
        
        // Create webset with phone number and contact enrichment focus
        const webset = await exa.websets.create({
            search: {
                query: `Adam Anzuoni phone number contact information professional profile business contact details email address`,
                count: 20,
                entity: { type: 'person' },
                criteria: [
                    { description: 'Phone number and direct contact information' },
                    { description: 'Professional email addresses and business contacts' },
                    { description: 'LinkedIn profile and social media presence' },
                    { description: 'Business affiliations and company information' },
                    { description: 'Professional directory listings and contact databases' }
                ]
            },
            enrichments: [
                {
                    description: 'Extract phone numbers including mobile, work, and personal contact numbers',
                    format: 'phone'
                },
                {
                    description: 'Find email addresses including professional and personal email contacts',
                    format: 'email'
                },
                {
                    description: 'Gather professional contact information including business addresses, LinkedIn profiles, and company affiliations',
                    format: 'text'
                },
                {
                    description: 'Identify social media profiles and online presence including Twitter, LinkedIn, GitHub, and personal websites',
                    format: 'text'
                }
            ],
            externalId: `adam-anzuoni-contact-${Date.now()}`,
            metadata: {
                project: 'ContactEnrichment',
                target: 'Adam Anzuoni',
                purpose: 'phone-number-discovery',
                requestedBy: 'user'
            }
        });

        console.log(`✅ Created webset: ${webset.id}`);
        console.log(`📊 Status: ${webset.status}`);
        
        // Add additional targeted searches
        await addPhoneNumberSearch(webset.id);
        await addProfessionalProfileSearch(webset.id);
        await addBusinessContactSearch(webset.id);
        
        return webset;
        
    } catch (error) {
        console.error('❌ Error creating webset:', error.message);
        throw error;
    }
}

async function addPhoneNumberSearch(websetId) {
    try {
        console.log('📞 Adding targeted phone number search...');
        
        const search = await exa.websets.searches.create(websetId, {
            query: `"Adam Anzuoni" phone number mobile contact telephone business phone work phone`,
            count: 15,
            entity: { type: 'person' },
            criteria: [
                { description: 'Direct phone number listings and contact databases' },
                { description: 'Business directory entries with phone numbers' },
                { description: 'Professional contact information and phone details' }
            ],
            behavior: 'append'
        });
        
        console.log(`✅ Added phone number search: ${search.id}`);
        
    } catch (error) {
        console.error('❌ Error adding phone search:', error.message);
    }
}

async function addProfessionalProfileSearch(websetId) {
    try {
        console.log('👤 Adding professional profile search...');
        
        const search = await exa.websets.searches.create(websetId, {
            query: `Adam Anzuoni LinkedIn profile professional background business contact information company email`,
            count: 10,
            entity: { type: 'person' },
            criteria: [
                { description: 'LinkedIn and professional social media profiles' },
                { description: 'Professional background and career information' },
                { description: 'Business email addresses and professional contacts' }
            ],
            behavior: 'append'
        });
        
        console.log(`✅ Added professional profile search: ${search.id}`);
        
    } catch (error) {
        console.error('❌ Error adding profile search:', error.message);
    }
}

async function addBusinessContactSearch(websetId) {
    try {
        console.log('💼 Adding business contact search...');
        
        const search = await exa.websets.searches.create(websetId, {
            query: `Adam Anzuoni business contact directory company information professional email phone number`,
            count: 10,
            entity: { type: 'person' },
            criteria: [
                { description: 'Business directory listings and contact information' },
                { description: 'Company affiliations and professional associations' },
                { description: 'Contact databases and professional directories' }
            ],
            behavior: 'append'
        });
        
        console.log(`✅ Added business contact search: ${search.id}`);
        
    } catch (error) {
        console.error('❌ Error adding business search:', error.message);
    }
}

async function monitorEnrichmentProgress(websetId) {
    console.log('📊 Monitoring contact enrichment progress...');
    
    const maxAttempts = 15;
    const delayMs = 20000; // 20 seconds
    
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
            const webset = await exa.websets.get(websetId);
            console.log(`\n🔄 Progress Check ${attempt}/${maxAttempts}:`);
            console.log(`   Status: ${webset.status}`);
            console.log(`   Searches: ${webset.searches.length}`);
            console.log(`   Enrichments: ${webset.enrichments.length}`);
            
            // Check search progress
            webset.searches.forEach((search, i) => {
                console.log(`   Search ${i+1}: ${search.status}`);
                if (search.progress) {
                    console.log(`     Found: ${search.progress.found}, Analyzed: ${search.progress.analyzed}`);
                    console.log(`     Completion: ${search.progress.completion}%`);
                }
            });
            
            // Check enrichment status
            webset.enrichments.forEach((enrichment, i) => {
                console.log(`   Enrichment ${i+1} (${enrichment.format}): ${enrichment.status}`);
            });
            
            if (webset.status === 'completed' || webset.status === 'idle') {
                console.log('✅ Contact enrichment completed!');
                return webset;
            }
            
            if (attempt < maxAttempts) {
                console.log(`   ⏳ Waiting ${delayMs/1000}s before next check...`);
                await new Promise(resolve => setTimeout(resolve, delayMs));
            }
            
        } catch (error) {
            console.error(`❌ Error checking progress (attempt ${attempt}):`, error.message);
        }
    }
    
    console.log('⚠️ Monitoring timeout reached. Enrichment may still be processing.');
}

async function exportContactResults(websetId) {
    try {
        console.log('📞 Exporting Adam Anzuoni contact results...');
        
        const webset = await exa.websets.get(websetId);
        
        // Try to get items using direct search equivalent
        const searchResults = await exa.searchAndContents('Adam Anzuoni phone number contact information', {
            numResults: 10
        });
        
        const results = {
            webset: {
                id: webset.id,
                status: webset.status,
                searches: webset.searches.length,
                enrichments: webset.enrichments.length,
                createdAt: webset.createdAt,
                metadata: webset.metadata
            },
            searches: webset.searches.map(search => ({
                id: search.id,
                query: search.query,
                status: search.status,
                progress: search.progress,
                criteria: search.criteria
            })),
            enrichments: webset.enrichments.map(enrichment => ({
                id: enrichment.id,
                format: enrichment.format,
                status: enrichment.status,
                description: enrichment.description
            })),
            searchResults: searchResults.results.map(result => ({
                title: result.title,
                url: result.url,
                content: result.text ? result.text.substring(0, 500) : null,
                publishedDate: result.publishedDate
            })),
            summary: {
                totalSearches: webset.searches.length,
                enrichmentTasks: webset.enrichments.length,
                directSearchResults: searchResults.results.length,
                phoneEnrichmentRequested: true,
                emailEnrichmentRequested: true
            }
        };
        
        const outputFile = `/Users/adamanzuoni/ReactionReach/adam_anzuoni_contact_enrichment_${Date.now()}.json`;
        fs.writeFileSync(outputFile, JSON.stringify(results, null, 2));
        
        console.log(`✅ Contact results exported to: ${outputFile}`);
        console.log(`📊 Direct search results: ${results.searchResults.length}`);
        console.log(`📞 Phone enrichment status: ${results.enrichments.find(e => e.format === 'phone')?.status || 'Not found'}`);
        console.log(`📧 Email enrichment status: ${results.enrichments.find(e => e.format === 'email')?.status || 'Not found'}`);
        
        // Display direct search findings
        if (searchResults.results.length > 0) {
            console.log('\n🔍 Direct Search Findings:');
            searchResults.results.forEach((result, i) => {
                console.log(`${i+1}. ${result.title}`);
                console.log(`   URL: ${result.url}`);
                if (result.text) {
                    // Look for phone patterns in content
                    const phonePatterns = result.text.match(/(\+?1[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})/g);
                    const emailPatterns = result.text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g);
                    
                    if (phonePatterns) {
                        console.log(`   📞 PHONE FOUND: ${phonePatterns.join(', ')}`);
                    }
                    if (emailPatterns) {
                        console.log(`   📧 EMAIL FOUND: ${emailPatterns.join(', ')}`);
                    }
                    
                    console.log(`   Content: ${result.text.substring(0, 200)}...`);
                }
                console.log('');
            });
        }
        
        return results;
        
    } catch (error) {
        console.error('❌ Error exporting contact results:', error.message);
        throw error;
    }
}

// Main execution
async function main() {
    try {
        // Check for API key
        if (!process.env.EXA_API_KEY) {
            console.error('❌ EXA_API_KEY environment variable required');
            console.log('💡 Set your API key: export EXA_API_KEY="your_key_here"');
            process.exit(1);
        }
        
        console.log('🔍 Adam Anzuoni Contact Enrichment with Exa');
        console.log('=' .repeat(50));
        
        // Create webset with contact enrichment
        const webset = await createAdamAnzuoniEnrichment();
        
        // Monitor progress
        await monitorEnrichmentProgress(webset.id);
        
        // Export results
        const results = await exportContactResults(webset.id);
        
        console.log('\n🎉 Adam Anzuoni Contact Enrichment Complete!');
        console.log(`📊 Webset ID: ${webset.id}`);
        console.log(`📞 Phone Enrichment: ${results.enrichments.find(e => e.format === 'phone') ? 'Requested' : 'Failed'}`);
        console.log(`📧 Email Enrichment: ${results.enrichments.find(e => e.format === 'email') ? 'Requested' : 'Failed'}`);
        console.log(`🔗 View webset at: https://dashboard.exa.ai/websets/${webset.id}`);
        
    } catch (error) {
        console.error('💥 Fatal error:', error.message);
        process.exit(1);
    }
}

// Export functions for module use
module.exports = {
    createAdamAnzuoniEnrichment,
    monitorEnrichmentProgress,
    exportContactResults
};

// Run if called directly
if (require.main === module) {
    main();
}