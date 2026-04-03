## Team

<style>
    .team-container {
        display: grid;
        column-gap: 3rem;
    }

    @media (max-width: 900px) {
        .team-container {
            grid-template-columns: 1fr;
        }
    }

    @media (min-width: 901px) {
        .team-container {
            grid-template-columns: 1fr 1fr;
        }
    }

    .team-member {
        display: grid;
        grid-template-columns: 1fr auto;
        align-items: start;
    }

    img {
        /* width: 150px; */
        width: 200px;
        width: 180px;
    }

    .member-info {
        padding: 0;
        padding-right: 0.8ch;
        padding-top:   0.5ch;
    }

    .member-photo {
        margin: 0;
        margin-right: 2ch;
        padding: 0;        
        padding-top:   0.5ch;
    }

</style>

<div class="team-container">
    <div class="team-member">
        <div class="member-info">
            <a href="https://www.zew.de/{{curLg|safe}}/team/fhe">Friedrich Heinemann </a> 
            Wissenschaftliche Leitung  
            <!-- Expertise in EU Institutionen <br>  -->
        </div>
        <div class="member-photo">
            <img src="/static/img/md/fhe.jpg">
        </div>
    </div>
    <div class="team-member">
        <div class="member-info">
            <a href="https://www.zew.de/{{curLg|safe}}/team/jkp">Jan Kemper </a> 
            Wissenschaftler<br> 
            LLM Konzeption  
        </div>
        <div class="member-photo">
            <img src="/static/img/md/jkp.jpg">
        </div>
    </div>
    <div class="team-member">
        <div class="member-info">
            <a href="https://www.zew.de/{{curLg|safe}}/team/cmb">Carlo Birkholz </a> 
            Wissenschaftler  
        </div>
        <div class="member-photo">
            <img src="/static/img/md/cmb.jpg">
        </div>
    </div>
    <div class="team-member">
        <div class="member-info">
            <a href="https://www.zew.de/{{curLg|safe}}/team/pau">Pascal Ausäderer </a> 
            Kommunikation  
        </div>
        <div class="member-photo">
            <img src="/static/img/md/pau.jpg">
        </div>
    </div>
    <div class="team-member">
        <div class="member-info">
            <a href="https://www.zew.de/{{curLg|safe}}/team/jgl">Julia Glashauser </a> 
            Kommunikation
        </div>
        <div class="member-photo">
            <img src="/static/img/md/jgl.jpg">
        </div>
    </div>
    <div class="team-member">
        <div class="member-info">
            <a href="https://www.zew.de/{{curLg|safe}}/team/pbu">Peter Buchmann </a> 
            Technik  
        </div>
        <div class="member-photo">
            <img src="/static/img/md/pbu.jpg">
        </div>
    </div>
</div>

<br>

[Impressum des ZEW](https://www.zew.de/en/legal-note)
