#!/usr/bin/env node

/**
 * Get Adam Anzuoni Phone Number via Apollo.io API
 * Using the MCP Apollo tools available in the system
 */

async function getAdamAnzuoniViaApollo() {
    try {
        console.log('🔍 Searching for Adam Anzuoni via Apollo API...');
        
        // First, try people search
        const searchResults = await searchPeopleApollo();
        if (searchResults) {
            console.log('✅ Found Adam via people search');
            return searchResults;
        }
        
        // If not found, try enrichment
        const enrichResults = await enrichPersonApollo();
        if (enrichResults) {
            console.log('✅ Found Adam via enrichment');
            return enrichResults;
        }
        
        // Try organization search for FUNDWELL
        const orgResults = await searchFundwellEmployees();
        if (orgResults) {
            console.log('✅ Found Adam via organization search');
            return orgResults;
        }
        
        return null;
        
    } catch (error) {
        console.error('❌ Apollo API error:', error.message);
        return null;
    }
}

async function searchPeopleApollo() {
    try {
        // Using Apollo people search for Adam Anzuoni at FUNDWELL
        const result = await global.mcpApollo.people_search({
            person_titles: ['Chief Technology Officer', 'CTO', 'Technology Officer'],
            q_organization_domains_list: ['fundwell.com', 'getfundwell.com']
        });
        
        console.log('Apollo People Search Results:', result);
        
        // Look for Adam Anzuoni in results
        if (result.people) {
            const adam = result.people.find(person => 
                person.first_name?.toLowerCase().includes('adam') && 
                (person.last_name?.toLowerCase().includes('anzuoni') || 
                 person.full_name?.toLowerCase().includes('anzuoni'))
            );
            
            if (adam) {
                console.log('🎯 Found Adam Anzuoni:');
                console.log(`   Name: ${adam.full_name || adam.first_name + ' ' + adam.last_name}`);
                console.log(`   Title: ${adam.title}`);
                console.log(`   Company: ${adam.organization?.name}`);
                console.log(`   Phone: ${adam.phone_numbers?.[0]?.sanitized_number || 'Not available'}`);
                console.log(`   Email: ${adam.email || 'Not available'}`);
                
                return adam;
            }
        }
        
        return null;
        
    } catch (error) {
        console.error('❌ Apollo people search error:', error.message);
        return null;
    }
}

async function enrichPersonApollo() {
    try {
        // Try to enrich Adam Anzuoni specifically
        const result = await global.mcpApollo.people_enrichment({
            first_name: 'Adam',
            last_name: 'Anzuoni',
            domain: 'fundwell.com',
            reveal_phone_number: true
        });
        
        console.log('Apollo Enrichment Results:', result);
        
        if (result.person) {
            const person = result.person;
            console.log('🎯 Enriched Adam Anzuoni:');
            console.log(`   Name: ${person.full_name}`);
            console.log(`   Phone: ${person.phone_numbers?.[0]?.sanitized_number || 'Not available'}`);
            console.log(`   Email: ${person.email || 'Not available'}`);
            
            return person;
        }
        
        return null;
        
    } catch (error) {
        console.error('❌ Apollo enrichment error:', error.message);
        return null;
    }
}

async function searchFundwellEmployees() {
    try {
        // Search for FUNDWELL organization first
        const orgResult = await global.mcpApollo.organization_search({
            q_organization_domains_list: ['fundwell.com', 'getfundwell.com']
        });
        
        console.log('Organization search results:', orgResult);
        
        if (orgResult.organizations && orgResult.organizations.length > 0) {
            const fundwell = orgResult.organizations[0];
            console.log(`Found organization: ${fundwell.name}`);
            
            // Now get employees
            const employeesResult = await global.mcpApollo.employees_of_company({
                company: 'FUNDWELL'
            });
            
            console.log('Employees results:', employeesResult);
            
            if (employeesResult.people) {
                const adam = employeesResult.people.find(person =>
                    person.first_name?.toLowerCase().includes('adam') &&
                    person.last_name?.toLowerCase().includes('anzuoni')
                );
                
                if (adam) {
                    return adam;
                }
            }
        }
        
        return null;
        
    } catch (error) {
        console.error('❌ Fundwell employees search error:', error.message);
        return null;
    }
}

async function getPersonEmail(apolloId) {
    try {
        if (!apolloId) return null;
        
        const result = await global.mcpApollo.get_person_email({
            apollo_id: apolloId
        });
        
        console.log('Email retrieval result:', result);
        return result;
        
    } catch (error) {
        console.error('❌ Get email error:', error.message);
        return null;
    }
}

async function main() {
    try {
        console.log('📞 Getting Adam Anzuoni Phone Number via Apollo API');
        console.log('=' .repeat(60));
        console.log('🎯 Target: Adam Anzuoni, CTO at FUNDWELL');
        console.log('📱 Expected: +14015758192');
        console.log('');
        
        // Import Apollo MCP tools
        if (typeof global.mcpApollo === 'undefined') {
            console.log('🔧 Setting up Apollo MCP integration...');
            // This would be handled by the MCP server
            console.log('❌ MCP Apollo tools not available in this context');
            console.log('💡 This script needs to be run with MCP Apollo server active');
            return;
        }
        
        const result = await getAdamAnzuoniViaApollo();
        
        if (result) {
            console.log('\n✅ SUCCESS! Found Adam Anzuoni via API');
            console.log('📊 Contact Information:');
            console.log(`   Name: ${result.full_name || result.first_name + ' ' + result.last_name}`);
            console.log(`   Phone: ${result.phone_numbers?.[0]?.sanitized_number || result.sanitized_phone || 'Not available'}`);
            console.log(`   Email: ${result.email || 'Not available'}`);
            console.log(`   Title: ${result.title}`);
            console.log(`   Company: ${result.organization?.name || result.company?.name}`);
            
            // If we have Apollo ID, try to get verified email
            if (result.id) {
                const emailResult = await getPersonEmail(result.id);
                if (emailResult) {
                    console.log(`   Verified Email: ${emailResult.email}`);
                }
            }
            
            // Save the result
            const fs = require('fs');
            const outputFile = `/Users/adamanzuoni/ReactionReach/adam_anzuoni_apollo_api_${Date.now()}.json`;
            fs.writeFileSync(outputFile, JSON.stringify(result, null, 2));
            console.log(`\n💾 Results saved to: ${outputFile}`);
            
        } else {
            console.log('\n❌ Could not find Adam Anzuoni via Apollo API');
            console.log('💡 Possible reasons:');
            console.log('   - Requires premium Apollo subscription');
            console.log('   - Phone number reveal needs special permissions');
            console.log('   - API rate limits or access restrictions');
            console.log('   - Need to authenticate with proper API key');
        }
        
    } catch (error) {
        console.error('💥 Fatal error:', error.message);
        process.exit(1);
    }
}

// Export for module use
module.exports = {
    getAdamAnzuoniViaApollo,
    searchPeopleApollo,
    enrichPersonApollo,
    searchFundwellEmployees
};

// Run if called directly
if (require.main === module) {
    main();
}